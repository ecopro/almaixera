# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMessage
from comandes.models import Soci


class Command(BaseCommand):
    help = "mostra llista d'emails dels socis d'una coope"

    def add_arguments(self, parser):
        #pass
        parser.add_argument('coope', nargs='+', type=str)

    def handle(self, *args, **options):
	#print options["coope"]
        coope = options["coope"][0]
        # Socis
        dest = []
        for e in Soci.objects.filter(cooperativa__nom=coope):
            if e.user.email:
                dest.append( e.user.email )
                print e.user.email

