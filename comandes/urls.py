from django.conf.urls import patterns, url

from comandes import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^fer_comanda', views.fer_comanda, name='fer_comanda'),
    url(r'^comandes', views.veure_comandes, name='comandes'),
    url(r'^caixa', views.caixa, name='caixa'),
    url(r'^pagament', views.pagament, name='pagament'),
)

