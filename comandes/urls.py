from django.conf.urls import patterns, url
from django.contrib.auth.views import password_reset, \
	password_reset_done, password_reset_confirm, password_reset_complete

from comandes import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^fer_comanda', views.fer_comanda, name='fer_comanda'),
    url(r'^esborra_comanda', views.esborra_comanda, name='esborra_comanda'),
    url(r'^comandes', views.veure_comandes, name='comandes'),
    url(r'^caixa', views.caixa, name='caixa'),
    url(r'^pagament', views.pagament, name='pagament'),
    url(r'^informe_proveidors', views.informe_proveidors, name='informe_proveidors'),
    url(r'^informe_caixes', views.informe_caixes, name='informe_caixes'),
    url(r'^test_email', views.test_email, name="test_email"),
    url(r'^recuperar_contrasenya/$', password_reset, name="recuperar_contrasenya"),
    url(r'^password_reset/$', password_reset, name="password_reset"),
    url(r'^password_reset_done/$', password_reset_done, name="password_reset_done"),
    url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', password_reset_confirm, name="password_reset_confirm"),
    url(r'^password_reset_complete/$', password_reset_complete, name="password_reset_complete"),
)

#http://stackoverflow.com/questions/21284672/django-password-reset-password-reset-confirm
