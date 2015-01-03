from django.contrib import admin
from models import *
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
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
    list_display = ('__unicode__','actiu','preu','granel','proveidor')
    search_fields = ('nom','proveidor__nom')
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
    list_display = ('user','cooperativa','get_superuser','get_groups')
    form = SociForm
    readonly_fields = ('user',)

    def get_superuser(self, obj):
        return obj.user.is_superuser
    get_superuser.short_description = "Super"
    get_superuser.admin_order_field = 'user__is_superuser'
    get_superuser.boolean = True
    def get_groups(self, obj):
        grps = ""
        for group in obj.user.groups.all():
            grps = grps + str(group)
        return grps
    get_groups.short_description = "Grups"
    get_groups.admin_order_field = 'user__groups'
    def get_form(self, request, obj=None, **kwargs):
        if not request.user.is_superuser:
            # fixem la coope si no es admin
            self.readonly_fields = ('user','cooperativa')
        soci_form = super(SociAdmin, self).get_form(request, obj, **kwargs)
        return soci_form
    def queryset( self, request ):
        qs = super(SociAdmin,self).queryset(request)
        # super-users can see all info
        if request.user.is_superuser:
            return qs
        # coopeadmin can see all users of his coope
        grp = Group.objects.get(name="coopeadmin")
        if grp in request.user.groups.all():
            coope = request.user.soci.cooperativa
            return qs.filter( cooperativa=coope )
        # non-admins only can edit their personal info
        return qs.filter( user=request.user )
    def save_model(self, request, soci, form, change):
        soci.save()
        user = soci.user
        user.first_name = form.cleaned_data['nom']
        user.last_name = form.cleaned_data['cognom']
        user.email = form.cleaned_data['email']
        user.save()
            
class AvisAdmin(admin.ModelAdmin):
    list_display = ('titol','data','cooperativa')
    ordering = ('data',)

# inline dels productes en els proveidors
class ProducteInline(admin.StackedInline):
	fieldsets = [
		(None,			{'fields': ['nom','actiu','proveidor','preu','granel'] }),
		('Mes info',	{'fields': ['stock','notes'], 'classes':['collapse'] }),
	]
	model = Producte
	extra = 1

class ProveidorAdmin(admin.ModelAdmin):
	inlines = [ProducteInline]

class CustomUserAdmin(UserAdmin):
	# TODO: forzar cooperativa a la del usuari actual
	
    def queryset(self, request ):
        users = super(CustomUserAdmin,self).queryset(request)
        # superuser can see all users
        if request.user.is_superuser:
            return users
        # coopeadmins can see their coope users and blank coope
        coope = request.user.soci.cooperativa
        exclude_ids = []
        for user in users:
            if hasattr(user,'soci') and user.soci.cooperativa!=coope:
                exclude_ids.append(user.id)
		users = users.exclude( id__in=exclude_ids )
        return users
    def save_model( self, request, user, form, change):
        # always staff members
        user.is_staff = True
        # avoid non-superusers creating superusers
        if not request.user.is_superuser:
            user.is_superuser = False
        user.save()
        # creem soci
        soci, creat = Soci.objects.get_or_create(user=user)
        # forzem coope del nou soci a la del usuari creador
        soci.cooperativa = request.user.soci.cooperativa
        soci.save()

class ActivacioAdmin(admin.ModelAdmin):
    list_display = ('cooperativa','proveidor','actiu','data')
    order = ('-data',)
    def get_form(self, request, obj=None, **kwargs):
        if not request.user.is_superuser:
            # fixem la coope si no es super
            self.readonly_fields = ('cooperativa',)
            #form.cleaned_data['cooperativa'] = request.user.soci.cooperativa
        form = super(ActivacioAdmin, self).get_form(request, obj, **kwargs)
        return form
    def save_model(self, request, obj, form, change):
        # fixem la coope si no es super
        if not request.user.is_superuser:
            obj.cooperativa = request.user.soci.cooperativa
        obj.save()

admin.site.unregister( User )
admin.site.register( User, CustomUserAdmin )

admin.site.register( GlobalConf )
admin.site.register( Avis, AvisAdmin )
admin.site.register( Cooperativa )
admin.site.register( Soci, SociAdmin )
admin.site.register( Proveidor, ProveidorAdmin )
admin.site.register( Producte, ProducteAdmin )
admin.site.register( Comanda, ComandaAdmin )
admin.site.register( DetallComanda, DetallAdmin )
admin.site.register( Activacio, ActivacioAdmin )
