from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.conf.urls.static import static
import settings
from django.contrib.auth.views import login, logout
from django1 import views as dj1views

urlpatterns = patterns('',
    # Examples:
    url(r'^$', dj1views.home, name='home'),
    # url(r'^django1/', include('django1.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls), name="siteadmin"),
    url(r'^comandes/', include('comandes.urls')),
    url(r'^accounts/login/$', login,{'template_name': 'login.html'}),
    url(r'^accounts/logout/$', logout,{'next_page': '/'}),
) #+ static( settings.STATIC_URL, document_root=settings.STATIC_ROOT)
