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
        # admin email per check
        admins = Soci.objects.filter( user__is_superuser=True )
        adminemails = [ admin.user.email for admin in admins ]
        # activacions
        activacions = ActivaProveidor.objects.filter(actiu=True)
        for act in activacions:
            # per cada activacio sabem proveidor i coope
            prov = act.proveidor
            coope = act.cooperativa
            if not prov or not coope:
                print "ERROR en ActivaProveidor: "+str(act)
                continue
            assumpte = "Comanda online cooperativa " + coope.nom
            data = propera_recollida(coope)

            # determinar si la propera recollida s'ha de fer (tancada)
            if not recollida_tancada(data,coope):
                #print "ENCARA NO TOCA! (cal tancar-la)"
                continue
            # no fer comanda si ja esta feta
            if act.darrera_comanda_notificada==data:
                print "Comanda ja realitzada"
                # TODO: TEST: activar-ho
                continue
            # guardem data darrera notificacio dp d'enviar email al final
            
            hihaproductes = False
            informe = ""
            contacte = ""
            detalls = DetallComanda.objects.filter(
                    producte__proveidor=prov,
                    comanda__data_recollida=data,
                    comanda__soci__cooperativa=coope )\
                    .values('producte__nom','producte__granel')\
                    .annotate(Sum('quantitat'))\
                    .order_by('producte__nom')
            # debug
            #print act, data
            # afegim productes al informe
            if len(detalls):
                informe += "\n" + "Cooperativa "+coope.nom.upper()+"\n"
            for detall in detalls:
                hihaproductes = True
                informe += detall['producte__nom']+" : "+unicode(detall['quantitat__sum'])
                if detall['producte__granel']:
                    informe += " kgs.\n"
                else:
                    informe += " unitats-manats\n"
            # afegim dades coopeadmins pel proveidor
            if hihaproductes:
                coopeadmins = Soci.objects.filter(cooperativa=coope,user__groups__name='coopeadmin')
                for coopeadmin in coopeadmins:
                    contacte += coopeadmin.user.first_name\
                            + " " + coopeadmin.user.email \
                            + u" , telèfon " + coopeadmin.telefon1 + "\n"
                    adminemails.append( coopeadmin.user.email )
                # determinar adreces d'email a enviar
                to_emails = []
                if act.auto_email_proveidor and prov.email:
                    to_emails.append( prov.email )
                if act.email:
                    to_emails.append( act.email )
                # Crea email
                data2 = data.strftime("%a, %d de %b")
                email = EmailMessage( assumpte, text %
                        (unicode(prov.nom),data2,informe,contacte) )
                email.cc = adminemails
                email.to = to_emails
                #debug
                #print email.message()
                # Envia email
                try:
                    if email.send():
                        print "EMAIL ENVIAT!"
                        # actualitzem data darrera notificacio si email OK
                        act.darrera_comanda_notificada = data
                        act.save()
                except:
                    print "ERROR enviant email"
                    
