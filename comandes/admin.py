from django.contrib import admin
from models import *

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

admin.site.register( Soci )
admin.site.register( Proveidor )
admin.site.register( Producte )
admin.site.register( Comanda, ComandaAdmin )
admin.site.register( DetallComanda, DetallAdmin )

