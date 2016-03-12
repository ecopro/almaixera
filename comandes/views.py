# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from comandes.models import *
from django.contrib.auth.decorators import login_required
from django import forms
from django.forms import ModelForm
from django.forms.formsets import formset_factory, BaseFormSet
from django.forms.models import modelformset_factory
from helpers import *
from datetime import datetime, date, timedelta
from django.db.models import Sum

"""
    FORMS
"""
class DetallForm(ModelForm):
    class Meta:
        model = DetallComanda
        fields = ['producte','quantitat']

class ProperesComandesForm(forms.Form):
    def __init__( self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProperesComandesForm,self).__init__( *args, **kwargs )
        coope = None
        if user:
			coope = user.soci.cooperativa
        choices = properes_comandes( coope )
        self.fields['data_recollida'] = forms.ChoiceField( choices=choices )

class ComandaForm(forms.Form):
    data_recollida = forms.DateField()

class InformeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(InformeForm, self).__init__(*args, **kwargs)
        choices = dates_informe( user.soci.cooperativa )
        # proper dia en la llista es la opcio per defecte
        avui = date.today()
        inicial = None
        if choices:
            inicial = choices[len(choices)-1]
        for data in choices:
            if data[0]>=str(avui):
                inicial = data[0]
            else:
                break
        self.fields['data_informe'] = forms.ChoiceField( choices=choices, initial=inicial )

def menu( request, missatge=None ):
    if not hasattr(request.user,'soci'):
        return render( request, 'nosoci.html' )
    coope = request.user.soci.cooperativa
    user = request.user
    remainingsecs = 0
    if coope:
        remainingsecs = (proper_tancament(coope)-datetime.now()).total_seconds()
    return render( request, 'menu.html', {
            "missatge" : missatge,
            "data_form" : ProperesComandesForm(request.POST, user=user),
            "super" : request.user.is_superuser,
            "prov_form" : InformeForm(request.POST, user=user),
            "caixes_form": InformeForm(request.POST, user=user),
            "proper_tancament": proper_tancament(coope),
            "remaining_secs": remainingsecs,
    } )

# filtrem llista de productes disponibles segons la coope de l'usuari visitant
from django.db.models import Q
def get_productes( request, data_recollida ):
    coope = request.user.soci.cooperativa
    # seleccionem proveidors actius per la coope
    activa_provs = ActivaProveidor.objects.filter(Q(data=None)|Q(data=data_recollida))\
                    .filter(cooperativa=coope,actiu=True)
    active_prod_ids = []
    # iterem proveidors actius
    for activa_prov in activa_provs:
        activa_prods = ActivaProducte.objects.filter(activa_proveidor=activa_prov,actiu=True)
        # iterem productes actius
        for activa_prod in activa_prods:
            active_prod_ids.append( activa_prod.producte.id )
    productes = Producte.objects\
                    .filter( actiu=True, stock=False, id__in=active_prod_ids )\
                    .extra(select={'lower_name':'lower(nom)'})\
                    .order_by('proveidor','lower_name')
    return productes

"""
    VIEWS
"""

@login_required
def index(request):
	# pagina principal
    return menu(request)

@login_required
def fer_comanda(request):
    if not hasattr(request.user,'soci'):
        return render( request, 'nosoci.html' )
    conf = request.user.soci.cooperativa
    if not conf:
		return menu(request,"Usuari sense coopearativa assignada: no es pot fer comanda.")
    dow_recollida = conf.dow_recollida
    data_recollida = request.GET.get("data_recollida")
    # comprovar dates comanda
    if type(data_recollida)==str or type(data_recollida)==unicode:
        try:
            data_recollida = datetime.strptime( data_recollida, "%Y-%m-%d" )
            if data_recollida.weekday()!=dow_recollida:
                return menu(request,"ERROR: data invalida (dow)")
        except:
            data_recollida = None
    if not (type(data_recollida)==date or type(data_recollida)==datetime):
        return menu(request,"ERROR: data invalida o inexistent")
    # comprovar tancament TEST
    coope = request.user.soci.cooperativa
    if recollida_tancada(data_recollida, coope):
        return menu(request,"ERROR: comanda tancada")

    # filtrar avisos per soci/coope
    avisos = Avis.objects.filter(data=request.GET.get("data_recollida")).filter(Q(cooperativa=coope)|Q(cooperativa=None))
    # filtrar llista de productes disponibles per cada coope
    productes = get_productes( request, data_recollida )
    
    #
    # PROCES COMANDA
    #
    if request.method=="POST":
        comanda_form = ComandaForm( request.POST )
        DetallsFormSet = formset_factory( DetallForm )
        detalls_formset = DetallsFormSet( request.POST )
        # filter products (and optimize! :)
        for form in detalls_formset:
            form.fields['producte'].queryset = productes
        user = request.user
        # TODO: check user (no cal: @login_required / no admins?)
        if not comanda_form.is_valid() or not detalls_formset.is_valid() or not user.is_active:
            return render( request, 'fer_comanda.html',
                    {   'form':comanda_form,
                        'formset':detalls_formset,
                        'avisos':avisos,
                        'productes':productes,
                        'missatge':"ERROR: dades incorrectes"} )
        else:
            # processem comanda
            soci = user.soci
            ara = datetime.now()
            dades_comanda = comanda_form.cleaned_data
            data_recollida = dades_comanda['data_recollida']

            # esborrar comanda previa si n'hi ha
            comanda = Comanda.objects.filter( soci=request.user.soci,
                            data_recollida=request.POST.get("data_recollida") )
            if comanda:
                comanda.delete() # esborra en cascada els detalls
            # creem comanda
            comanda = Comanda(soci=soci,
                              data_creacio=ara,
                              data_recollida=data_recollida, )
            comanda.save()
            # guardem detall productes
            nprods = 0
            for item in detalls_formset:
                dades = item.cleaned_data
                if dades.get('producte') and dades.get('quantitat'):
                    detall = DetallComanda(
                        producte = dades.get('producte'),
                        quantitat = dades.get('quantitat'),
                        comanda = comanda)
                    detall.save()
                    nprods += 1
            # if items==0 esborrar comanda
            if nprods<=0:
                comanda.delete() # detalls en cascada (inexistents)
            # TODO: if 2 items repetits, unir-los
            #return render( request, 'menu.html', {"data_form":ProperesDatesForm(),
            #                        "missatge":"Comanda realitzada correctament."} )
            return menu(request,"Comanda realitzada correctament")
    #
    # RENDER FORM
    #
    # form amb data prefixada (readonly)
    elif request.method=="GET":
        # data form (comanda)
        comanda_form = ComandaForm( request.GET )
        # camp de data amagat (form en format compacte, display llegible)
        comanda_form.fields['data_recollida'].widget.attrs['readonly'] = True
        comanda_form.fields['data_recollida'].widget.attrs['hidden'] = True
        # detalls: els traiem de la BBDD
        # data_recollida testejada al ppi de la view
        comanda = Comanda.objects.filter( soci=request.user.soci,
                        data_recollida=request.GET.get("data_recollida"))
        detalls = DetallComanda.objects.filter( comanda=comanda )
        # transformar objectes en diccionaris per reconstruir menu
        detalls_dicts = []
        for item in detalls:
            # transformen attrs en dict
            detall = item.__dict__
            # arreglem IDs
            detall['producte'] = detall['producte_id']
            detalls_dicts.append( detall )
        # generem form i omplim amb dades amb initial
        DetallsFormSet = formset_factory( DetallForm, extra=23 )
        detalls_formset = DetallsFormSet( initial=detalls_dicts )
        # filtrar productes disponibles
        # A mes, accelera la query de render del formset!!! :)
        # (tots els forms de la request tenen el mateix set de productes
        for form in detalls_formset:
            form.fields['producte'].queryset = productes
    return render( request, 'fer_comanda.html',
            {   'form':comanda_form,
                'formset':detalls_formset,
                'avisos':avisos,
                'productes':productes,
            } )

@login_required
def veure_comandes(request):
    if not hasattr(request.user,'soci'):
        return render( request, 'nosoci.html' )
    user = request.user
    soci = user.soci
    # si soci: veu les seves comandes
    avui = date.today()
    desde = avui-timedelta(31)
    fins = avui+timedelta(31)
    increment = 0.0
    if request.user.soci:
        increment = float(request.user.soci.cooperativa.increment_preu)
    comandes = Comanda.objects.filter(soci=soci,
            data_recollida__range=[desde,fins]).order_by('-data_recollida')
    # si coopeadmin veu totes les comandes de la setmana (dels seus socis)
    grp = Group.objects.get(name="coopeadmin")
    if grp in request.user.groups.all():
        desde = avui-timedelta(8)
        fins = avui+timedelta(1)
        # llista de socis de la coope
        socis = Soci.objects.filter(cooperativa=request.user.soci.cooperativa)
        comandes = Comanda.objects.filter(soci__in=socis,
                data_recollida__range=[desde,fins]).order_by('-data_recollida')
    # main loop
    for comanda in comandes:
        total_demanat = 0
        total_rebut = 0
        detalls = DetallComanda.objects.filter(comanda=comanda)
        comanda.detalls = detalls
        # TODO: filtrar aqui enlloc de al template (ara "tancada" li indica al templ)
        comanda.tancada = recollida_tancada( comanda.data_recollida, soci.cooperativa )
        subtotal_demanat = 0
        subtotal_rebut = 0
        for detall in detalls:
            subtotal_demanat = float(detall.producte.preu)*detall.quantitat
            subtotal_rebut = float(detall.producte.preu)*detall.quantitat_rebuda
            detall.subtotal_demanat = subtotal_demanat
            detall.subtotal_rebut = subtotal_rebut
            total_demanat += subtotal_demanat
            total_rebut += subtotal_rebut
        comanda.total_demanat = total_demanat
        comanda.total_rebut = total_rebut
        comanda.total_demanat_incr = total_demanat * (1+increment/100)
        comanda.total_rebut_incr = total_rebut * (1+increment/100)
    return render( request, 'comandes.html', {"comandes":comandes,"increment":increment} )

@login_required
def esborra_comanda(request):
    if not hasattr(request.user,'soci'):
        return render( request, 'nosoci.html' )
    user = request.user
    soci = user.soci
    # esborrar nomes comandes no tancades
    data_recollida = request.GET.get("data_recollida")
    # comprovar tancament
    if type(data_recollida)==str or type(data_recollida)==unicode:
        data_recollida = datetime.strptime( data_recollida, "%Y-%m-%d" )
    if recollida_tancada(data_recollida, soci.cooperativa):
        return menu(request,"ERROR: comanda tancada")
    # avanti!
    data_recollida = request.GET.get("data_recollida")
    confirma = request.POST.get("confirma")
    if not data_recollida:
        data_recollida = request.POST.get("data_recollida")
        if not data_recollida:
            return render( request, 'menu.html', {"missatge":"ERROR: No s'ha esborrat la comanda."})
    comanda = Comanda.objects.filter( soci=soci, data_recollida=data_recollida )
    if comanda and confirma:
        comanda.delete()
        #return render( request, 'menu.html', {"missatge":"Comanda esborrada correctament."} )
        return menu(request,"comanda esborrada correctament")
    # confirma esborrat
    return render( request, 'esborra_comanda.html',
                   {"data_recollida":data_recollida,
                    #"missatge":"ERROR: en comanda="+str(comanda)+" confirma="+str(confirma)
                    })


"""
    ADMIN VIEWS
"""

@login_required
def informe_proveidors( request ):
    if not hasattr(request.user,'soci'):
        return render( request, 'nosoci.html' )
    # data informe
    data = datetime.strptime( request.GET.get('data_informe'), "%Y-%m-%d" )
    # METODE 1: subqueries
    """proveidors = Proveidor.objects.all()
    for prov in proveidors:
        detalls = DetallComanda.objects.filter(
                producte__proveidor=prov,
                comanda__data_recollida=data )\
                .values('producte__nom')\
                .annotate( Sum("quantitat") )\
                .order_by('producte__proveidor')
        prov.detalls = detalls"""
    ## METODE 2: 1 sola query. agrupem en el template
    # annotate: agrupa les comandes del mateix producte d'un mateix soci
    coope = request.user.soci.cooperativa
    productes = DetallComanda.objects.filter(
            comanda__data_recollida=data )\
            .values('producte__nom','producte__proveidor__nom',
                'producte__proveidor__email','producte__proveidor__email2',
                'producte__granel','producte__proveidor__telefon1',)\
            .annotate( Sum("quantitat") )\
            .order_by('producte__proveidor__nom')
    if coope:
        productes = productes.filter( comanda__soci__cooperativa=coope )
    return render( request, 'informe_proveidors.html',
                    {"data":data,"productes":productes,"cooperativa":coope} )

# dades per informes
def detalls_informe_caixes( data, coope, producte=None ):
    # METODE 2: 1 sola query, agrupem en el template
    detalls = DetallComanda.objects.filter(
            comanda__data_recollida=data, )\
            .values('producte__nom','producte__id',
                'producte__granel',
                'producte__preu',
                'producte__proveidor__nom',
                'comanda__soci__num_caixa','quantitat',
                'comanda__soci__user__username',
                'comanda__soci__user__first_name',
                'comanda__soci__user__last_name',
                'comanda__soci__cooperativa',
                'comanda','producte','quantitat','quantitat_rebuda')\
            .order_by('producte__nom','comanda__soci__num_caixa')
    if producte:
        detalls = detalls.filter( producte=producte )
    if coope:
        detalls = detalls.filter( comanda__soci__cooperativa=coope )
    return detalls

@login_required    
def informe_caixes( request ):
    if not hasattr(request.user,'soci'):
        return render( request, 'nosoci.html' )
    # data informe
    data = datetime.strptime( request.GET.get('data_informe'), "%Y-%m-%d" )
    coope = request.user.soci.cooperativa
    detalls = detalls_informe_caixes( data, coope )
    # calculem subtotals (iterant, de moment)
    for detall in detalls:
        qs = detalls.filter(producte__nom=detall['producte__nom'])
        t1 = qs.annotate(Sum('quantitat'))
        total = 0
        for elem in qs:
            total += elem['quantitat']
        detall['total'] = total
    return render( request, 'informe_caixes.html',
                    {"data":data,"productes":detalls,"cooperativa":coope} )

#http://stackoverflow.com/questions/10567845/how-to-use-the-built-in-password-reset-view-in-django
@login_required
def test_email( request ):
    from django.core.mail import EmailMessage
    email = EmailMessage('Hello', 'World', to=['emieza@xtec.cat'])
    email.send()
    return HttpResponse( "Enviant email" )
    
#http://stackoverflow.com/questions/17968781/how-to-add-button-next-to-add-user-button-in-django-admin-site
@login_required
def afegeix_proveidors( request ):
    if not hasattr(request.user,'soci'):
        return render( request, 'nosoci.html' )
    regenera_activacions( request )
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
    
class DetallFormComplet(ModelForm):
    class Meta:
        model = DetallComanda
        exclude = ['comanda','producte','quantitat']
        #fields = ['quantitat','quantitat_rebuda','preu_rebut']

@login_required
def distribueix_productes( request, data_recollida, producte ):
    if not hasattr(request.user,'soci'):
        return render( request, 'nosoci.html' )
    data = data_recollida
    producte_obj = Producte.objects.get(id=producte)
    coope = request.user.soci.cooperativa
    # generem dades pel form
    #detalls = detalls_informe_caixes( data, coope, producte_obj )
    detalls = DetallComanda.objects.filter(
                comanda__data_recollida=data, producte=producte_obj)\
                .order_by('comanda__soci__num_caixa')
    if coope:
        detalls = detalls.filter( comanda__soci__cooperativa=coope )
    # creem formset class
    DetallsFormSet = modelformset_factory( DetallComanda, form=DetallFormComplet, extra=0 )
    # processem dades
    if request.method=="POST":
        # valors retornats: actualitzar
        detalls_formset = DetallsFormSet( request.POST )
        # processar formset si valid i salvar detalls
        if not detalls_formset.is_valid():
            return render( request, 'distribueix_producte.html',
                        {"producte": producte_obj, "data":data,
                        "detalls_formset":detalls_formset,
                        "missatge": "ERROR: dades incorrectes"} )
        else:
            # processar formset valid
            for detall in detalls_formset.forms:
                detall.save()
    else:
        # generem form i omplim dades amb initial/queryset
        detalls_formset = DetallsFormSet( queryset=detalls )

    # ajustar camps de nomes-lectura i dades a mostrar afegides
    for detall_form in detalls_formset:
        # dades afegides per mostrar
        detall_id = detall_form['id'].value()
        detall_obj = DetallComanda.objects.get(id=detall_id)
        detall_form.num_caixa = detall_obj.comanda.soci.num_caixa
        detall_form.soci = "("+detall_obj.comanda.soci.user.username+") " \
                        + detall_obj.comanda.soci.user.first_name +" " \
                        + detall_obj.comanda.soci.user.last_name
        detall_form.quant = detall_obj.quantitat
        # camps de nomes-lectura
        #detall_form.fields['quantitat'].widget.attrs['readonly'] = True
    return render( request, 'distribueix_producte.html',
                {"producte": producte_obj, "data":data,
                "detalls_formset":detalls_formset} )

