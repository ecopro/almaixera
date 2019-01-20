from django.conf.urls import include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.conf.urls.static import static
from . import settings
from django.contrib.auth.views import LoginView, LogoutView
from django1 import views as dj1views

urlpatterns = [
    # Examples:
    url(r'^$', dj1views.home, name='home'),
    # url(r'^django1/', include('django1.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', admin.site.urls, name="siteadmin"),
    url(r'^comandes/', include('comandes.urls')),
    url(r'^accounts/login/$', LoginView.as_view(template_name='login.html')),
    url(r'^accounts/logout/$', LogoutView.as_view(next_page='/')),
 ] #+ static( settings.STATIC_URL, document_root=settings.STATIC_ROOT)
