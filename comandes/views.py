# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render
from comandes.models import *
from django.contrib.auth.decorators import login_required
from django import forms
from django.forms import ModelForm
from django.forms.formsets import formset_factory, BaseFormSet
from helpers import properes_comandes, dates_informe, recollida_tancada
from multiform import MultiForm
from datetime import datetime, date, timedelta
from django.db.models import Sum

"""
    FORMS
"""

class DetallForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super(DetallForm,self).__init__(*args,**kwargs)
        #self.fields["producte"].queryset = self.fields["producte"].queryset.exclude(actiu=False)
        self.fields["producte"].queryset = \
            Producte.objects.filter(actiu=True).extra(select={'lower_name':'lower(nom)'}).order_by('lower_name')
    class Meta:
        model = DetallComanda
        fields = ['producte','quantitat']

class ProperesComandesForm(forms.Form):
    #data_recollida = forms.ChoiceField( choices = properes_dates_recollida() )
    # TODO: acotar dates disponibles
    def __init__( self, *args, **kwargs):
        super(ProperesComandesForm,self).__init__( args, kwargs )
        choices = properes_comandes()
        self.fields['data_recollida'] = forms.ChoiceField( choices=choices )

class ComandaForm(forms.Form):
    data_recollida = forms.DateField()

#class InformeForm(forms.Form):
#    data_informe = forms.ChoiceField( choices = dates_informe() )
class InformeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(InformeForm, self).__init__(*args, **kwargs)
        choices = dates_informe()
        # proper dia en la llista es la opcio per defecte
        avui = date.today()
        inicial = len(choices)-1
        for i,data in reversed(list(enumerate(choices))):
            if data[0]>str(avui):
                inicial = data[0]
            else:
                break
        self.fields['data_informe'] = forms.ChoiceField( choices=choices, initial=inicial )

def menu( request, missatge=None ):
    return render( request, 'menu.html', {
            "missatge" : missatge,
            "data_form" : ProperesComandesForm,
            "super" : request.user.is_superuser,
            "prov_form" : InformeForm,
            "caixes_form": InformeForm
    } )

"""
    VIEWS
"""

@login_required
def index(request):
    # TODO: menu
    #  - fer torn caixes
    return menu(request)

@login_required
def fer_comanda(request):
    conf = GlobalConf.objects.get()
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
    # comprovar tancament
    if recollida_tancada(data_recollida):
        return menu(request,"ERROR: comanda tancada")

    # PROCES COMANDA
    if request.method=="POST":
        comanda_form = ComandaForm( request.POST )
        DetallsFormSet = formset_factory( DetallForm )
        detalls_formset = DetallsFormSet( request.POST )
        user = request.user
        # TODO: check user (no cal: @login_required / no admins?)
        if not comanda_form.is_valid() or not detalls_formset.is_valid() or not user.is_active:
            print comanda_form.is_valid()
            print detalls_formset.is_valid()
            #return menu(request,"ERROR: dades incorrectes")
            return render( request, 'form.html', {'form':comanda_form,
                                                  'formset':detalls_formset,
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

    # RENDER FORM

    # dafalut forms
    # TODO: no extra sino JS amb afegir prod.
    detalls_formset = formset_factory( DetallForm, extra=30 )
    # data a triar (choice)
    comanda_form = ProperesComandesForm()
    # form amb data prefixada (readonly)
    if request.method=="GET":
        """
            Forms amb data prefixada (del menu anterior)
        """
        if request.GET.get("data_recollida"):
            # data form (comanda)
            comanda_form = ComandaForm( request.GET )
            # camp de data amagat (form en format compacte, display llegible)
            comanda_form.fields['data_recollida'].widget.attrs['readonly'] = True
            comanda_form.fields['data_recollida'].widget.attrs['hidden'] = True
            # detalls: els traiem de la BBDD
            comanda = Comanda.objects.filter( soci=request.user.soci,
                                              data_recollida=request.GET.get("data_recollida")
                                            )
            detalls = DetallComanda.objects.filter( comanda=comanda )
            # trasnformar objectes en diccionaris per reconstruir menu
            detalls_dicts = []
            for item in detalls:
                # transformen attrs en dict
                detall = item.__dict__
                # arreglem IDs
                detall['producte'] = detall['producte_id']
                detalls_dicts.append( detall )
            # generem form i omplim amb dades
            DetallsFormSet = formset_factory( DetallForm, extra=30 )
            detalls_formset = DetallsFormSet( initial=detalls_dicts )
        # TODO: invalidar si no posem data? (anular defaults)
    # TODO: filtrar avisos per soci/coope
    avisos = Avis.objects.filter( data=request.GET.get("data_recollida") )
    return render( request, 'form.html', {'form':comanda_form,'formset':detalls_formset,'avisos':avisos} )


@login_required
def veure_comandes(request):
    user = request.user
    soci = user.soci
    # TODO: check user
    avui = date.today()
    desde = avui-timedelta(31)
    fins = avui+timedelta(31)
    comandes = Comanda.objects.filter(soci=soci,
            data_recollida__range=[desde,fins]).order_by('-data_recollida')
    for comanda in comandes:
        total = 0
        detalls = DetallComanda.objects.filter(comanda=comanda)
        comanda.detalls = detalls
        comanda.tancada = recollida_tancada( comanda.data_recollida )
        subtotal = 0
        for detall in detalls:
            subtotal = float(detall.producte.preu)*detall.quantitat
            detall.subtotal = subtotal
            total += subtotal
        comanda.total = total
    return render( request, 'comandes.html', {"comandes":comandes} )


@login_required
def esborra_comanda(request):
    # esborrar nomes comandes no tancades
    data_recollida = request.GET.get("data_recollida")
    # comprovar tancament
    if type(data_recollida)==str or type(data_recollida)==unicode:
        data_recollida = datetime.strptime( data_recollida, "%Y-%m-%d" )
    if recollida_tancada(data_recollida):
        return menu(request,"ERROR: comanda tancada")
    # avanti!
    user = request.user
    soci = user.soci
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

@login_required
def caixa(request):
    return HttpResponse("Torn de caixa: ...")


@login_required
def pagament(request):
    return HttpResponse("Pagament: ...")


"""
    ADMIN VIEWS
"""

# TODO: super required
@login_required
def informe_proveidors( request ):
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
    productes = DetallComanda.objects.filter(
            comanda__data_recollida=data )\
            .values('producte__nom','producte__proveidor__nom',
                'producte__proveidor__email','producte__granel',
                'producte__proveidor__telefon1',)\
            .annotate( Sum("quantitat") )\
            .order_by('producte__proveidor__nom')
    return render( request, 'informe_proveidors.html', {"data":data,"productes":productes} )

@login_required    
def informe_caixes( request ):
    # data informe
    data = datetime.strptime( request.GET.get('data_informe'), "%Y-%m-%d" )
    ## METODE 2: 1 sola query. agrupem en el template
    detalls = DetallComanda.objects.filter(
            comanda__data_recollida=data )\
            .values('producte__nom','producte__granel','producte__proveidor__nom',
                'comanda__soci__num_caixa','quantitat',
                'comanda__soci__user__first_name',
                'comanda__soci__user__last_name')\
            .order_by('producte__nom','comanda__soci__num_caixa')
    """# TODO: subtotals amb annotate
    subtotals = DetallComanda.objects.filter(
                comanda__data_recollida=data ).annotate( Sum("quantitat") )
    print subtotals"""
    # calculem subtotals (iterant, de moment)
    for detall in detalls:
        qs = detalls.filter(producte__nom=detall['producte__nom'])
        t1 = qs.annotate(Sum('quantitat'))
        total = 0
        for elem in qs:
            total += elem['quantitat']
        detall['total'] = total
    return render( request, 'informe_caixes.html', {"data":data,"productes":detalls} )

#http://stackoverflow.com/questions/10567845/how-to-use-the-built-in-password-reset-view-in-django
@login_required
def test_email( request ):
    from django.core.mail import EmailMessage
    email = EmailMessage('Hello', 'World', to=['emieza@xtec.cat'])
    email.send()
    return HttpResponse( "Enviant email" )
    
    