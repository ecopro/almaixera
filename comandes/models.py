from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

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

class GlobalConf(SingletonModel):
    # dow = Day Of Week (weekday, dilluns=0, dimarts=1, etc)
    dow_recollida = models.IntegerField(default=1) # dimarts per defecte
    dow_tancament = models.IntegerField(default=4) # divendres per defecte


class Soci(models.Model):
    user = models.OneToOneField(User)
    num_caixa = models.IntegerField(default=0)
    dni = models.CharField(max_length=10)
    direccio = models.CharField(max_length=200)
    cp = models.CharField(max_length=8)
    poblacio = models.CharField(max_length=200)
    # User ja te email
    telefon1 = models.CharField(max_length=9)
    telefon2 = models.CharField(max_length=9,blank=True)
    telefon3 = models.CharField(max_length=9,blank=True)
    def __unicode__(self):
        return self.user.username
        
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = Soci.objects.get_or_create(user=instance)  

post_save.connect(create_user_profile, sender=User) 
    
class Proveidor(models.Model):
    nom = models.CharField(max_length=200)
    cif = models.CharField(max_length=10)
    direccio = models.CharField(max_length=200)
    cp = models.CharField(max_length=8)
    poblacio = models.CharField(max_length=200)
    email = models.EmailField(max_length=200,blank=True)
    telefon1 = models.CharField(max_length=9)
    telefon2 = models.CharField(max_length=9,blank=True)
    telefon3 = models.CharField(max_length=9,blank=True)
    def __unicode__(self):
        return self.nom

class Producte(models.Model):
    nom = models.CharField(max_length=200)
    proveidor = models.ForeignKey(Proveidor)
    preu = models.DecimalField(max_digits=5,decimal_places=2,default=0.0)
    stock = models.BooleanField(default=False)
    granel = models.BooleanField(default=True)
    def __unicode__(self):
        return self.nom

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
        
