from django.contrib import admin
from models import *
from django.contrib.auth.models import User
from django import forms

class DetallAdmin(admin.ModelAdmin):
    # FK with getters
    list_display = ('data_recollida','nom','cognom','producte','quantitat','proveidor')
    # FK with "__"
    search_fields = ('quantitat','producte__nom','comanda__data_recollida','producte__proveidor__nom','comanda__soci__user__username','comanda__soci__user__first_name')
    # filter by user
    def queryset( self, request):
        qs = super(DetallAdmin, self).queryset(request)
        if request.user.is_superuser:
            # superuser no filtrat
            return qs
        # TODO: filtrar comandes ja tancades
        # filtrar usuari
        return qs.filter( comanda__soci=request.user.soci )

class ComandaAdmin(admin.ModelAdmin):
    # filter by user
    def queryset( self, request):
        user = request.user
        qs = super(ComandaAdmin, self).queryset(request)
        # admin sees everything
        if user.is_superuser:
            return qs
        # not admin: filter
        # TODO: filtrar comandes ja tancades
        return qs.filter( soci=request.user.soci )


def activa(modeladmin, request, queryset):
    queryset.update(actiu=True)
activa.short_description = "Activa els productes"

def desactiva(modeladmin, request, queryset):
    queryset.update(actiu=False)
desactiva.short_description = "Desctiva els productes"

class ProducteAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','actiu','preu','granel','proveidor')#'__unicode__'
    list_editable = ('actiu',)
    ordering = ('nom',)
    actions = [ activa , desactiva ]

"""
    SOCIS: nom, cognom i email estan al model auth.User
    Creem custom form i copiem els camps al User enlloc del Soci
"""
class SociForm(forms.ModelForm):
    # TODO: order added fields to the top
    nom = forms.CharField()
    cognom = forms.CharField()
    email = forms.EmailField()
    initial_fields = ['nom','cognom','email']
    class Meta:
        model = Soci
    def __init__(self, *args, **kwargs):
        super(SociForm, self).__init__(*args, **kwargs)
        # load data from user
        if 'instance' in kwargs.keys():
            soci = kwargs['instance']
            self.fields['nom'].initial = soci.user.first_name
            self.fields['cognom'].initial = soci.user.last_name
            self.fields['email'].initial = soci.user.email
        
class SociAdmin(admin.ModelAdmin):
    form = SociForm
    readonly_fields = ('user','cooperativa')

    def get_form(self, request, obj=None, **kwargs):
        # Exclude changes from num_caixa if not admin
        self.exclude = []
        if not request.user.is_superuser:
            pass
            # de moment deshabilitat TODO: habilitar
            #self.exclude.append('num_caixa')
            # el de aqui a baix no va, dona error com camp a completar
            #soci_form = super(SociAdmin, self).get_form(request, obj, **kwargs)
            #soci_form.base_fields['num_caixa'].widget.attrs['disabled'] = True
        soci_form = super(SociAdmin, self).get_form(request, obj, **kwargs)
        return soci_form
    def queryset( self, request ):
        qs = super(SociAdmin,self).queryset(request)
        # super-users can see all info
        if request.user.is_superuser:
            return qs
        # non-admins only can edit their personal info
        return qs.filter( user=request.user )
    def save_model(self, request, soci, form, change):
        soci.save()
        user = soci.user
        user.first_name = form.cleaned_data['nom']
        user.last_name = form.cleaned_data['cognom']
        user.email = form.cleaned_data['email']
        user.save()
            
""" # No cal per l'usuari: nomes accessible per l'admin
class UserAdmin(admin.ModelAdmin):
    def queryset(self, request ):
        qs = super(UserAdmin,self).queryset(request)
        # super-users can see all info
        if request.user.is_superuser:
            return qs
        # non-admins only can edit their personal info
        return qs.filter( id=request.user.id )

admin.site.unregister( User )
admin.site.register( User, UserAdmin )"""

admin.site.register( GlobalConf )
admin.site.register( Cooperativa )
admin.site.register( Soci, SociAdmin )
admin.site.register( Proveidor )
admin.site.register( Producte, ProducteAdmin )
admin.site.register( Comanda, ComandaAdmin )
admin.site.register( DetallComanda, DetallAdmin )

