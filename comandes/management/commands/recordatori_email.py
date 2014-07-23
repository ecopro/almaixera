# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMessage
from comandes.models import GlobalConf, Soci

dows = ['dilluns','dimarts','dimecres','dijous','divendres','dissabte','diumenge']

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        pass
        #parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        conf = GlobalConf.objects.get()
        dow_tancament = dows[ conf.dow_tancament ]
        hora_tancament = conf.hora_tancament.strftime('%H:%m')
        text = """
Hola %s,

aquest email és un recordatori perquè facis la comanda de la setmana que ve. No et despistis!
La propera comanda es tanca %s a les %s h,

Per fer la comanda vés a www.almaixera.cat

Comissió d'informàtica responsable de l'Almàixera :)
""" % ("Almaixerenc@", dow_tancament, hora_tancament )
        assumpte = "Recordatori per fer comanda"
        email = EmailMessage( assumpte, text )
        # Socis
        dest = []
        for e in Soci.objects.all():
            if e.user.email:
                dest.append( e.user.email )
        # Envia email
        email.bcc = dest #['emieza@xtec.cat']
        #print email.message() # debug
        email.send()

