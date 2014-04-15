# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render
from comandes.models import *
from django.contrib.auth.decorators import login_required
from django import forms
from django.forms import ModelForm
from django.forms.formsets import formset_factory, BaseFormSet
from helpers import properes_dates_recollida
from multiform import MultiForm
from datetime import datetime
from django.db.models import Count,Sum

"""
    FORMS
"""

class DetallForm(ModelForm):
    class Meta:
        model = DetallComanda
        fields = ['producte','quantitat']

class ProperesDatesForm(forms.Form):
    data_recollida = forms.ChoiceField( choices = properes_dates_recollida())
    # TODO: acotar dates disponibles (constructor?)
    #def __init__( self, user, *args, **kwargs):
    #    super(ComandaForm,self).__init__( args, kwargs )
    #    choices = properes_dates_recollida( user )

class ComandaForm(forms.Form):
    data_recollida = forms.DateField()


"""
    VIEWS
"""

@login_required
def index(request):
    # TODO: menu
    #  - fer comanda
    #  - modificar comanda
    #  - anular comanda
    #  - canviar data
    #  - fer torn caixes
    dates = ProperesDatesForm()
    return render( request, 'menu.html', {"data_form":dates,"super":request.user.is_superuser} )


@login_required
def fer_comanda(request):

    # PROCES COMANDA
    if request.method=="POST":
        comanda_form = ComandaForm( request.POST )
        DetallsFormSet = formset_factory( DetallForm )
        detalls_formset = DetallsFormSet( request.POST )
        user = request.user
        # TODO: check user (no cal: @login_required / no admins?)
        if comanda_form.is_valid() and detalls_formset.is_valid() and user.is_active:
            # processem comanda
            soci = user.soci
            ara = datetime.now()
            dades_comanda = comanda_form.cleaned_data
            # esborrar comanda previa si n'hi ha
            comanda = Comanda.objects.filter( soci=request.user.soci,
                                              data_recollida=request.POST.get("data_recollida") )
            if comanda:
                comanda.delete() # esborra en cascada els detalls
            # creem comanda
            data_recollida = dades_comanda['data_recollida']
            if type(dades_comanda['data_recollida'])==str:
                data_recollida = datetime.strptime( dades_comanda['data_recollida'], "%Y-%m-%d" )
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
            return render( request, 'menu.html', {"missatge":"Comanda realitzada correctament."} )

    # RENDER FORM

    # dafalut forms
    # TODO: no extra sino JS amb afegir prod.
    detalls_formset = formset_factory( DetallForm, extra=30 )
    # data a triar (choice)
    comanda_form = ProperesDatesForm()
    # form amb data prefixada (readonly)
    if request.method=="GET":
        """
            Forms amb data prefixada (del menu anterior)
        """
        if request.GET.get("data_recollida"):
            # data form (comanda)
            comanda_form = ComandaForm( request.GET )
            comanda_form.fields['data_recollida'].widget.attrs['readonly'] = True
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

    return render( request, 'form.html', {'form':comanda_form,'formset':detalls_formset} )


@login_required
def veure_comandes(request):
    user = request.user
    soci = user.soci
    # TODO: check user
    comandes = Comanda.objects.filter(soci=soci).order_by('data_recollida')
    for comanda in comandes:
        detalls = DetallComanda.objects.filter(comanda=comanda)
        comanda.detalls = detalls
    context = {"comandes":comandes}
    return render(request,'comandes.html',context)

@login_required
def esborra_comanda(request):
    # TODO: esborrar nomes si estem dins dels terminis (comandes futures)
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
        return render( request, 'menu.html', {"missatge":"Comanda esborrada correctament."} )
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
    #detalls = DetallComanda.objects.filter( ).order_by( 'producte__proveidor' )
    dates = properes_dates_recollida()
    detalls = DetallComanda.objects.filter(comanda__data_recollida=dates[0][0]).values('producte').annotate( Sum("quantitat") ).order_by('producte__proveidor')
    return render( request, 'informe_proveidors.html', {"productes":detalls} )

@login_required    
def informe_caixes( request ):
    return HttpResponse("informe_caixes")
