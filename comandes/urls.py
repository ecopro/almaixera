from django.conf.urls import url
from django.urls import path
from django.contrib.auth.views import \
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView, LoginView, LogoutView

from comandes import views
from comandes.class_views.boxes_report import BoxesReportView

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^fer_comanda', views.fer_comanda, name='fer_comanda'),
    url(r'^esborra_comanda', views.esborra_comanda, name='esborra_comanda'),
    url(r'^comandes', views.veure_comandes, name='comandes'),
    url(r'^informe_proveidors', views.informe_proveidors, name='informe_proveidors'),
    url(r'^informe_caixes_old', views.informe_caixes, name='informe_caixes'),
    path(r'informe_caixes', BoxesReportView.as_view(), name='boxes_report'),
    url(r'^test_email', views.test_email, name="test_email"),
    url(r'^recuperar_contrasenya/$', PasswordResetView.as_view(), name="recuperar_contrasenya"),
    url(r'^password_reset/$', PasswordResetView.as_view(), name="password_reset"),
    url(r'^password_reset_done/$', PasswordResetDoneView.as_view(), name="password_reset_done"),
    url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    url(r'^password_reset_complete/$', PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    url(r'^afegeix_proveidors/', views.afegeix_proveidors, name="afegeix_proveidors" ),
    url(r'^distribueix_productes/(?P<data_recollida>[0-9-]+)/(?P<producte>\w{0,50})/$', views.distribueix_productes, name="distribueix_productes" ),
    url(r'^accounts/login/$', LoginView.as_view(template_name='login.html'), name='login'),
    url(r'^accounts/logout/$', LogoutView.as_view(next_page='/')),
    #{'next_page': '/'}),
]

#http://stackoverflow.com/questions/21284672/django-password-reset-password-reset-confirm
# change SITE_ID in settings.py
