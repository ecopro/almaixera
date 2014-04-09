from django.contrib import admin
from models import *

class DetallAdmin(admin.ModelAdmin):
    # FK with getters
    list_display = ('data_recollida','soci','producte','quantitat','proveidor')
    # FK with "__"
    search_fields = ('quantitat','producte__nom','comanda__data_recollida','producte__proveidor__nom')


admin.site.register( Soci )
admin.site.register( Proveidor )
admin.site.register( Producte )
admin.site.register( Comanda )
admin.site.register( DetallComanda, DetallAdmin )

