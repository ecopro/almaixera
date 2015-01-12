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
    def get_queryset( self, request):
        qs = super(DetallAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            # superuser no filtrat
            return qs
        # TODO: filtrar comandes ja tancades
        # filtrar usuari
        return qs.filter( comanda__soci=request.user.soci )

class ComandaAdmin(admin.ModelAdmin):
    # filter by user
    def get_queryset( self, request):
        user = request.user
        qs = super(ComandaAdmin, self).get_queryset(request)
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
            # proteccio pel 1r super fet des de comanda
            if hasattr(soci,'user'):
                self.fields['nom'].initial = soci.user.first_name
                self.fields['cognom'].initial = soci.user.last_name
                self.fields['email'].initial = soci.user.email
        
class SociAdmin(admin.ModelAdmin):
    list_display = ('user','cooperativa','get_groups','get_actiu')
    form = SociForm
    readonly_fields = ('user',)
    def get_actiu(self,obj):
        return obj.user.is_active
    get_actiu.short_description = "Actiu"
    get_actiu.admin_order_field = "user__is_active"
    get_actiu.boolean = True
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
        else:
            self.readonly_fields = ()
        soci_form = super(SociAdmin, self).get_form(request, obj, **kwargs)
        return soci_form
    def get_queryset( self, request ):
        qs = super(SociAdmin,self).get_queryset(request)
        # super-users can see all info (+superuser status)
        if request.user.is_superuser:
            self.list_display = ('user','cooperativa','get_superuser','get_groups')
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
    def get_queryset(self, request):
        qs = super(AvisAdmin,self).get_queryset(request)
        # si super retorna tot
        if request.user.is_superuser:
            return qs
        # coopeadmins nomes poden veure avisos de la seva coope
        coope = request.user.soci.cooperativa
        qs = qs.filter(cooperativa=coope)
        return qs
    def get_form(self, request, obj=None, **kwargs):
        if not request.user.is_superuser:
            # fixem la coope si no es admin
            self.readonly_fields = ('cooperativa',)
        form = super(AvisAdmin, self).get_form(request, obj, **kwargs)
        return form
    def save_model(self, request, avis, form, change):
        if not request.user.is_superuser:
            # fixem la coope si no es admin
            avis.cooperativa = request.user.soci.cooperativa
        avis.save()

# inline dels productes en els proveidors
class ProducteInline(admin.StackedInline):
	fieldsets = [
		(None,			{'fields': ['nom','preu','actiu'] }),
		('Mes info',	{'fields': ['stock','granel','notes'], 'classes':['collapse'] }),
	]
	model = Producte
	extra = 1

class ProveidorAdmin(admin.ModelAdmin):
	inlines = [ProducteInline]

from django.contrib.admin.util import flatten_fieldsets
class CustomUserAdmin(UserAdmin):
    list_display = ('username','first_name','last_name','email',
                    'is_active','is_superuser','get_groups')
    # visualitzacio
    def get_groups(self, obj):
        grps = ""
        for group in obj.groups.all():
            grps = grps + str(group)
        return grps
    get_groups.short_description = "Grups"
    get_groups.admin_order_field = 'user__groups'
    def get_queryset(self, request):
        users = super(CustomUserAdmin,self).get_queryset(request)
        # superuser can see all users
        if request.user.is_superuser:
            return users
        # coopeadmins can only see their coope users
        coope = request.user.soci.cooperativa
        #TODO: filter(soci__cooperativa=coope) easier!
        exclude_ids = []
        for user in users:
            if hasattr(user,'soci') and user.soci.cooperativa!=coope:
                exclude_ids.append(user.id)
		users = users.exclude( id__in=exclude_ids )
        return users
    # form i detall
    def get_form(self, request, obj=None, **kwargs):
        if not request.user.is_superuser:
            self.readonly_fields = ('is_staff','is_superuser','groups','user_permissions',)
        return super(CustomUserAdmin,self).get_form(request,obj,**kwargs)
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
    ordering = ('proveidor__nom',)
    list_editable = ('actiu','data')
    actions = [ activa, desactiva ]
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
    def get_queryset(self, request):
        activacions = super(ActivacioAdmin,self).get_queryset(request)
        # si super retorna tot
        if request.user.is_superuser:
            return activacions
        # coopeadmins nomes poden veure restriccions de la seva coope
        coope = request.user.soci.cooperativa
        activacions = activacions.filter(cooperativa=coope)
        return activacions

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
