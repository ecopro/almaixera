# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMessage
from django.db.models import Sum
from comandes.models import *
from comandes.helpers import *
import locale, time

locale.setlocale(locale.LC_TIME,"ca_ES.utf8")
dows = ['dilluns','dimarts','dimecres','dijous','divendres','dissabte','diumenge']

class Command(BaseCommand):
    help = 'Envia email de comanda als proveidors'

    def add_arguments(self, parser):
        pass
        #parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        text = u"""
Benvolgut/da %s,

Aquest és un email automàtic amb la comanda requerida per les cooperatives associades a ALMAIXERA.CAT

Data de comanda: %s

%s

Si hi hagués cap problema, contacti sisplau amb:

%s

Merci
"""
        assumpte = "Comanda online cooperatives almaixera.cat"
        data = propera_recollida()
        # admin email per check
        admins = Soci.objects.filter( user__is_superuser=True )
        adminemails = [ admin.user.email for admin in admins ]
        # Proveidors
        dest = []
        for prov in Proveidor.objects.all():
            #print prov
            hihaproductes = False
            informe = ""
            contacte = ""
            # Creem informe de productes per proveidor i coope
            for coope in Cooperativa.objects.all():
                hihaproductescoope = False
                #print "\t"+str(coope)
                detalls = DetallComanda.objects.filter(
                        producte__proveidor=prov,
                        comanda__data_recollida=data,
                        comanda__soci__cooperativa=coope )\
                        .values('producte__nom')\
                        .annotate(Sum('quantitat'))\
                        .order_by('producte__nom')
                # afegim productes al informe
                if len(detalls):
                    informe += "\n" + "COOPERTIVA "+coope.nom+"\n"
                for detall in detalls:
                    hihaproductes = True
                    hihaproductescoope = True
                    informe += detall['producte__nom']+" : "+unicode(detall['quantitat__sum'])+"\n"
                #if hihaproductes: print "\t\t"+str(hihaproductes)
                # afegim dades coopeadmin
                if hihaproductescoope:
                    coopeadmins = Soci.objects.filter(cooperativa=coope,user__groups__name='coopeadmin')
                    for coopeadmin in coopeadmins:
                        contacte += coope.nom + ": " + coopeadmin.user.first_name\
                                + " " + coopeadmin.user.email \
                                + " telf=" + coopeadmin.telefon1 + "\n"
            if prov.email and hihaproductes:
                # Crea email
                data2 = data.strftime("%a, %d de %b")
                email = EmailMessage( assumpte, text %
                        (unicode(prov.nom),data2,informe,contacte) )
                dest.append( prov.email )
                email.cc = adminemails
                email.to = [prov.email]
                email.to = ['emieza@xtec.cat']
                # Envia email
                #print email.message() # debug
                email.send()

