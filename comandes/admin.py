from django.contrib import admin
from models import *
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django import forms
from datetime import datetime
from helpers import regenera_activacions

class DetallInline(admin.TabularInline):
    model = DetallComanda
    extra = 1

# NO l'utilitzem pq fem servir el Detall inline a Comanda
class DetallAdmin(admin.ModelAdmin):
    # FK with getters
    list_display = ('data_recollida','nom','cognom','producte','quantitat','proveidor')
    search_fields = ('quantitat','producte__nom','comanda__data_recollida','producte__proveidor__nom','comanda__soci__user__username','comanda__soci__user__first_name')
    # filter by user
    def get_queryset( self, request):
        qs = super(DetallAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            # superuser no filtrat
            return qs
        # TODO: filtrar comandes ja tancades
        # filtrar coope usuari (per coopeadmins,
        # usuaris normals no poden veure-ho)
        return qs.filter( comanda__soci__cooperativa=request.user.soci.cooperativa )

class ComandaAdmin(admin.ModelAdmin):
    inlines = [ DetallInline ]
    list_display = ('soci','data_recollida','data_creacio',)
    ordering = ('-data_recollida','soci',)
    search_fields = ('soci','data_recollida',)
    # filter by user
    def get_queryset( self, request):
        user = request.user
        qs = super(ComandaAdmin, self).get_queryset(request)
        # admin sees everything
        if user.is_superuser:
            return qs
        # not admin: filter
        return qs.filter( soci__cooperativa=request.user.soci.cooperativa )

def activa(modeladmin, request, queryset):
    queryset.update(actiu=True)
activa.short_description = "Activa els productes"
def desactiva(modeladmin, request, queryset):
    queryset.update(actiu=False)
desactiva.short_description = "Desctiva els productes"

class ProducteAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','actiu','preu','granel','stock','proveidor')
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
            grps = grps + str(group) + " "
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
        # el user esta en grup "socis" al crear-se
        user.save()

class CoopeAdmin(admin.ModelAdmin):
    #list_display = ('titol','data','cooperativa')
    #ordering = ('data',)
    def get_queryset(self, request):
        qs = super(CoopeAdmin,self).get_queryset(request)
        # si super retorna tot
        if request.user.is_superuser:
            return qs
        # coopeadmins nomes poden veure la seva coope
        coope = request.user.soci.cooperativa
        qs = qs.filter(id=coope.id)
        return qs
        
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
        (None,          {'fields': ['nom','preu','actiu'] }),
        ('Mes info',    {'fields': ['stock','granel','notes'], 'classes':['collapse'] }),
    ]
    model = Producte
    extra = 1

class ProveidorAdmin(admin.ModelAdmin):
    list_display = ('nom','poblacio','email','telefon1',)
    inlines = [ProducteInline]
    def get_form(self, request, obj=None, **kwargs):
        if not request.user.is_superuser:
            pass
            # fixem la coope si no es super
            #self.readonly_fields = ('cooperativa',)
            #form.cleaned_data['cooperativa'] = request.user.soci.cooperativa
        form = super(ProveidorAdmin, self).get_form(request, obj, **kwargs)
        return form
    def save_model(self, request, obj, form, change):
        # fixem la coope si no es super
        if not request.user.is_superuser:
            obj.cooperativa = request.user.soci.cooperativa
        obj.save()
        
from django.contrib.admin.util import flatten_fieldsets
class CustomUserAdmin(UserAdmin):
    list_display = ('username','first_name','last_name','email',
                    'is_active','is_superuser','get_groups')
    # visualitzacio
    def get_groups(self, obj):
        grps = ""
        for group in obj.groups.all():
            grps = grps + str(group) + " "
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
        # forzem coope del nou soci a la del usuari creador (coopeadmin)
        if not request.user.is_superuser:
            soci.cooperativa = request.user.soci.cooperativa
        soci.save()
        # ficar nou soci dins grup "socis"
        gsocis, creat = Group.objects.get_or_create(name="socis")
        gsocis.user_set.add( user )

class ActivaProdInline(admin.TabularInline):
    model = ActivaProducte
    readonly_fields = ('producte','cooperativa')
    fields = ('actiu','data','cooperativa','producte')
    #exclude = ('notes',)
    extra = 0
    def get_queryset(self,request):
        qs = super(ActivaProdInline,self).get_queryset(request)
        # nomes mostrem els productes que el proveidor ha activat
        qs = qs.filter( producte__actiu=True )
        return qs

class ActivaProdInactiuInline(admin.TabularInline):
    model = ActivaProducte
    verbose_name = "Producte desactivat pel proveidor"
    verbose_name_plural = "Productes DESACTIVATS pel proveidor"
    readonly_fields = ('producte','cooperativa','actiu','data','cooperativa')
    fields = ('actiu','data','cooperativa','producte')
    extra = 0
    def get_queryset(self,request):
        qs = super(ActivaProdInactiuInline,self).get_queryset(request)
        # nomes mostrem els productes que el proveidor ha activat
        qs = qs.filter( producte__actiu=False )
        return qs
    
class ActivaProveidorAdmin(admin.ModelAdmin):
    inlines = [ ActivaProdInline, ActivaProdInactiuInline ]
    list_display = ('proveidor','cooperativa','actiu','data','email','auto_email_proveidor','get_email_proveidor')
    ordering = ('proveidor__nom',)
    list_editable = ('actiu','data')
    readonly_fields = ('proveidor',)
    actions = [ activa, desactiva ]
    def get_form(self, request, obj=None, **kwargs):
        if not request.user.is_superuser:
            # fixem la coope si no es super
            self.readonly_fields = ('proveidor','cooperativa')
            #form.cleaned_data['cooperativa'] = request.user.soci.cooperativa
        form = super(ActivaProveidorAdmin, self).get_form(request, obj, **kwargs)
        return form
    def save_model(self, request, obj, form, change):
        # fixem la coope si no es super
        if not request.user.is_superuser:
            obj.cooperativa = request.user.soci.cooperativa
        obj.save()
    def get_queryset(self, request):
        # regenera tot
        regenera_activacions( request )
        # procedim...
        activacions = super(ActivaProveidorAdmin,self).get_queryset(request)
        # si super retorna tot
        if request.user.is_superuser:
            return activacions
        # coopeadmins nomes poden veure restriccions de la seva coope
        coope = request.user.soci.cooperativa
        activacions = activacions.filter(cooperativa=coope)
        return activacions
    def get_email_proveidor(self,obj):
		return obj.proveidor.email
    get_email_proveidor.short_description = "Email proveidor"

class ActivaProducteAdmin(admin.ModelAdmin):
    list_display = ('producte','actiu','activa_proveidor','cooperativa','get_producte_actiu')
    list_editable = ('actiu',)
    ordering = ('activa_proveidor','producte__nom')
    search_fields = ('activa_proveidor__proveidor__nom','producte__nom')
    actions = ( activa, desactiva )
    def get_queryset(self, request):
        activacions = super(ActivaProducteAdmin,self).get_queryset(request)
        # si super retorna tot
        if request.user.is_superuser:
            return activacions
        # coopeadmins nomes poden veure restriccions de la seva coope
        coope = request.user.soci.cooperativa
        activacions = activacions.filter(cooperativa=coope)
        return activacions
    def get_producte_actiu(self, obj):
        return obj.producte.actiu
    get_producte_actiu.short_description = "Activat pel proveidor"
		

class ComandaStockForm(forms.ModelForm):
    class Meta:
        model = ComandaStock
    def __init__(self, *args, **kwargs):
        super(ComandaStockForm,self).__init__(*args, **kwargs)
        # filtrem productes de stock
        # TODO: filtrar productes activats en la coope
        self.fields['producte'].queryset = Producte.objects.filter(stock=True)

class ComandaStockAdmin(admin.ModelAdmin):
    list_display = ('producte','soci','quantitat','data_creacio')
    search_fields = ('producte__nom',)
    #list_editable = ('quantitat',)
    form = ComandaStockForm
    def get_form(self, request, obj=None, **kwargs):
        # els socis nomes poden fer comandes per ells mateixos
        if not request.user.is_superuser:
            self.readonly_fields = ('soci','data_creacio')
        form = super(ComandaStockAdmin, self).get_form(request, obj, **kwargs)
        return form
    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.soci = request.user.soci
            obj.data_creacio = datetime.now()
        obj.save()
    def get_queryset(self, request):
        comandes = super(ComandaStockAdmin,self).get_queryset(request)
        # users can see all comandes-stock of its coope
        if not request.user.is_superuser:
            comandes = comandes.filter(soci__cooperativa=request.user.soci.cooperativa)
        return comandes

admin.site.unregister( User )
admin.site.register( User, CustomUserAdmin )

admin.site.register( Avis, AvisAdmin )
admin.site.register( Cooperativa, CoopeAdmin )
admin.site.register( Soci, SociAdmin )
admin.site.register( Proveidor, ProveidorAdmin )
admin.site.register( Producte, ProducteAdmin )
admin.site.register( Comanda, ComandaAdmin )
#admin.site.register( DetallComanda, DetallAdmin )
admin.site.register( ActivaProveidor, ActivaProveidorAdmin )
admin.site.register( ActivaProducte, ActivaProducteAdmin )
admin.site.register( ComandaStock, ComandaStockAdmin )

