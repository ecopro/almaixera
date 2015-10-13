# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.validators import MaxValueValidator, MinValueValidator

dies_setmana = list(enumerate(("dilluns","dimarts","dimecres","dijous","divendres","dissabte","diumenge")))

import datetime

# Create your models here.

class SingletonModel(models.Model):
    class Meta:
        abstract = True
    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super(SingletonModel, self).save(*args, **kwargs)
    @classmethod
    def load(cls):
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()

class Cooperativa(models.Model):
    nom = models.CharField( max_length=200 )
    notes = models.TextField( blank=True )
    # dow = Day Of Week (weekday, dilluns=0, dimarts=1, etc)
    dow_recollida = models.IntegerField( default=1, choices=dies_setmana,
                        validators=[MinValueValidator(0),MaxValueValidator(6)] ) # dimarts per defecte
    dow_tancament = models.IntegerField( default=4, choices=dies_setmana,
                        validators=[MinValueValidator(0),MaxValueValidator(6)] ) # divendres per defecte
    hora_tancament = models.TimeField( default=datetime.time(14,0) ) # 2 del migdia
    num_setmanes_previsio = models.IntegerField( default=4 )
    # mes dades s'inclouen en l'usuari coopeadmin enlloc d'aqui
    def __unicode__(self):
        return self.nom

class Avis(models.Model):
    titol = models.CharField(max_length=200)
    text = models.TextField()
    data = models.DateField()
    user = models.ForeignKey(User,null=True,blank=True)
    cooperativa = models.ForeignKey(Cooperativa,null=True,blank=True,
                         help_text="Si es deixa en blanc es mostrarà l'avís a totes les cooperatives.")

# Soci es crea aparellat amb User (OneToOne)
# dit d'altra manera, es una extensió del model del Django User
class Soci(models.Model):
    user = models.OneToOneField( User )
    cooperativa = models.ForeignKey( Cooperativa, blank=True, null=True, default=None)
    num_caixa = models.IntegerField( default=0, help_text="Ull, ha de concordar amb el login username." )
    dni = models.CharField( max_length=10, blank=True )
    direccio = models.CharField( max_length=200 )
    cp = models.CharField( max_length=8 )
    poblacio = models.CharField( max_length=200 )
    # User ja te email
    telefon1 = models.CharField(max_length=9)
    telefon2 = models.CharField(max_length=9,blank=True)
    telefon3 = models.CharField(max_length=9,blank=True)
    notes = models.TextField(blank=True)
    def __unicode__(self):
        return self.user.username


class Proveidor(models.Model):
    user = models.OneToOneField(User,blank=True,null=True,default=None)
    nom = models.CharField(max_length=200)
    cif = models.CharField(max_length=10,blank=True)
    direccio = models.CharField(max_length=200,blank=True)
    cp = models.CharField(max_length=8,blank=True)
    poblacio = models.CharField(max_length=200,blank=True)
    email = models.EmailField(max_length=200,blank=True,
        help_text="adreça on s'enviarà l'email de comanda (proveidor o responsable de la coope)")
    email2 = models.EmailField(max_length=200,blank=True,
        help_text="email de contacte (no s'enviarà email de comanda)")
    telefon1 = models.CharField(max_length=30)
    telefon2 = models.CharField(max_length=30,blank=True)
    telefon3 = models.CharField(max_length=30,blank=True)
    notes = models.TextField(blank=True)
    def __unicode__(self):
        return self.nom

class Producte(models.Model):
    nom = models.CharField(max_length=200)
    actiu = models.BooleanField(default=True)
    proveidor = models.ForeignKey(Proveidor)
    preu = models.DecimalField(max_digits=5,decimal_places=2,default=0.0)
    stock = models.BooleanField(default=False,
        help_text="Activa perquè el producte aparegui a la comanda de stock. Desactiva perquè aparegui a la comanda setmanal.")
    granel = models.BooleanField(default=True,
        help_text="Actiu = €/kg | Inactiu = €/unitat-manat")
    notes = models.TextField(blank=True)
    # ordre de les querys
    ordering = ('nom',)
    def __unicode__(self):
        mostra = self.nom + " [" + str(self.preu)
        if self.granel:
            mostra += u" \u20AC/kg]"
        else:
            mostra += u" \u20AC/unitat-manat]"
        mostra += " ("+self.proveidor.nom+")"
        return mostra

class Comanda(models.Model):
    soci = models.ForeignKey(Soci)
    data_creacio = models.DateTimeField('data creacio')
    data_recollida = models.DateField('data recollida')
    preu_rebut = models.DecimalField(max_digits=5,decimal_places=2,default=0.0)
    def __unicode__(self):
        return unicode(self.data_recollida)+u" - "+unicode(self.soci)


from django.core.exceptions import ValidationError

def valida_no_zero(value):
    if value == 0:
        raise ValidationError('aquest camp no pot ser zero')

class DetallComanda(models.Model):
    producte = models.ForeignKey(Producte)
    quantitat = models.FloatField(default=0, validators=[valida_no_zero] )
    comanda = models.ForeignKey(Comanda)
    quantitat_rebuda = models.FloatField(default=0)
    preu_rebut = models.DecimalField(max_digits=5,decimal_places=2,default=0.0)
    def __unicode__(self):
        return unicode(self.comanda)+u" - "+unicode(self.producte.nom)+u" ("+unicode(self.quantitat)+")"
    # getters per admin
    def data_recollida(self):
        return self.comanda.data_recollida
    def soci(self):
        return self.comanda.soci
    def nom(self):
        return self.comanda.soci.user.first_name
    def cognom(self):
        return self.comanda.soci.user.last_name
    def proveidor(self):
        return self.producte.proveidor
    def username(self):
        return self.comanda.soci.user.username


class ComandaStock(models.Model):
    producte = models.ForeignKey(Producte)
    soci = models.ForeignKey(Soci)
    data_creacio = models.DateTimeField('data creacio')
    quantitat = models.FloatField(default=0, validators=[valida_no_zero] )
    quantitat_rebuda = models.FloatField(default=0)
    preu_rebut = models.DecimalField(max_digits=5,decimal_places=2,default=0.0)
    class Meta:
        unique_together = ('producte','soci')

# Activa proveidors per cada coope
class ActivaProveidor(models.Model):
    proveidor = models.ForeignKey(Proveidor)
    cooperativa = models.ForeignKey(Cooperativa)
    actiu = models.BooleanField(default=True)
    data = models.DateField("data d'activacio",blank=True,null=True,
                help_text="Optatiu, per si vols activar un proveidor només per una data.")
    email = models.EmailField("email comanda",max_length=200,blank=True,null=True,
                help_text="adreça on s'enviarà l'email de comanda (proveidor o responsable de la coope)")
    auto_email_proveidor = models.BooleanField(default=False,
                help_text="enviar email automàtic al proveidor")
    notes = models.TextField(blank=True)
    def __unicode__(self):
        return unicode(self.proveidor)+u" | "+unicode(self.cooperativa)

class ActivaProducte(models.Model):
    producte = models.ForeignKey(Producte)
    activa_proveidor = models.ForeignKey(ActivaProveidor)
    cooperativa = models.ForeignKey(Cooperativa)
    actiu = models.BooleanField(default=True)
    data = models.DateField("data d'activacio",blank=True,null=True,
                    help_text="Optatiu, per si vols activar un proveidor només per una data.")
    notes = models.TextField(blank=True)
    def __unicode__(self):
        return unicode(self.producte)+u" "+unicode(self.cooperativa)
	def get_producteactiu(self):
		return self.producte.actiu
	get_producteactiu.short_description = "Actiu pel proveidor"
	
