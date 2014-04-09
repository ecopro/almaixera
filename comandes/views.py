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

"""class ComandaForm(ModelForm):
    class Meta:
        model = Comanda
        fields = ['data_recollida']
        widgets = {
            'data_recollida': forms.Select( choices=properes_dates_recollida() )
        }
"""

class DetallForm(ModelForm):
    class Meta:
        model = DetallComanda
        fields = ['producte','quantitat']

class ComandaForm(forms.Form):
    # acotar dates disponibles (constructor?)
    data_recollida = forms.ChoiceField( choices=properes_dates_recollida() )


@login_required
def index(request):
    # TODO: menu
    #  - fer comanda
    #  - modificar comanda
    #  - anular comanda
    #  - canviar data
    #  - fer torn caixes
    return render(request,'menu.html')

@login_required
def fer_comanda(request):
    if request.method=="POST":
        comanda_form = ComandaForm( request.POST )
        DetallsFormSet = formset_factory( DetallForm )
        detalls_formset = DetallsFormSet( request.POST )

        user = request.user
        # TODO: check user
        if comanda_form.is_valid() and detalls_formset.is_valid() and user.is_active:
            # processem comanda
            user = request.user
            soci = user.soci
            ara = datetime.now()
            dades_comanda = comanda_form.cleaned_data
            dades_detalls = detalls_formset.cleaned_data
            # creem comanda
            comanda = Comanda(soci=soci,
                              data_creacio=ara,
                              data_recollida=datetime.strptime( dades_comanda['data_recollida'], "%Y-%m-%d" )
            )
            comanda.save()
            # detall productes
            for item in detalls_formset:
                dades = item.cleaned_data
                if dades.get('producte') and dades.get('quantitat'):
                    detall = DetallComanda(
                        producte = dades.get('producte'),
                        quantitat = dades.get('quantitat'),
                        comanda = comanda
                    )
                    detall.save()
            # TODO: if items==0 esborrar comanda
            return render( request, 'menu.html', {"missatge":"Comanda realitzada correctament."} )
            #HttpResponse("Comanda feta per usuari="+str(user.soci))
    else:
        comanda_form = ComandaForm()
        #detalls_formset = formset_factory( formset=BaseFormSet, extra=10 )
    
    comanda_form = ComandaForm()
    detalls_formset = formset_factory( DetallForm, extra=10 )
    
    return render(request,'form.html',{'comanda_form':comanda_form,'detalls_formset':detalls_formset})
    
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
def caixa(request):
    return HttpResponse("Torn de caixa: ...")


@login_required
def pagament(request):
    return HttpResponse("Pagament: ...")

