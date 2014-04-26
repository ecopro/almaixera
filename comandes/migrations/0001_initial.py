# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GlobalConf'
        db.create_table(u'comandes_globalconf', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dow_recollida', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('dow_tancament', self.gf('django.db.models.fields.IntegerField')(default=4)),
            ('num_setmanes_previsio', self.gf('django.db.models.fields.IntegerField')(default=4)),
        ))
        db.send_create_signal(u'comandes', ['GlobalConf'])

        # Adding model 'Soci'
        db.create_table(u'comandes_soci', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('num_caixa', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('dni', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('direccio', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('cp', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('poblacio', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('telefon1', self.gf('django.db.models.fields.CharField')(max_length=9)),
            ('telefon2', self.gf('django.db.models.fields.CharField')(max_length=9, blank=True)),
            ('telefon3', self.gf('django.db.models.fields.CharField')(max_length=9, blank=True)),
        ))
        db.send_create_signal(u'comandes', ['Soci'])

        # Adding model 'Proveidor'
        db.create_table(u'comandes_proveidor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('cif', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('direccio', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('cp', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('poblacio', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=200, blank=True)),
            ('telefon1', self.gf('django.db.models.fields.CharField')(max_length=9)),
            ('telefon2', self.gf('django.db.models.fields.CharField')(max_length=9, blank=True)),
            ('telefon3', self.gf('django.db.models.fields.CharField')(max_length=9, blank=True)),
        ))
        db.send_create_signal(u'comandes', ['Proveidor'])

        # Adding model 'Producte'
        db.create_table(u'comandes_producte', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('proveidor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['comandes.Proveidor'])),
            ('preu', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=5, decimal_places=2)),
            ('stock', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('granel', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'comandes', ['Producte'])

        # Adding model 'Comanda'
        db.create_table(u'comandes_comanda', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('soci', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['comandes.Soci'])),
            ('data_creacio', self.gf('django.db.models.fields.DateTimeField')()),
            ('data_recollida', self.gf('django.db.models.fields.DateField')()),
            ('preu_rebut', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=5, decimal_places=2)),
        ))
        db.send_create_signal(u'comandes', ['Comanda'])

        # Adding model 'DetallComanda'
        db.create_table(u'comandes_detallcomanda', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('producte', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['comandes.Producte'])),
            ('quantitat', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('comanda', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['comandes.Comanda'])),
            ('quantitat_rebuda', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('preu_rebut', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=5, decimal_places=2)),
        ))
        db.send_create_signal(u'comandes', ['DetallComanda'])


    def backwards(self, orm):
        # Deleting model 'GlobalConf'
        db.delete_table(u'comandes_globalconf')

        # Deleting model 'Soci'
        db.delete_table(u'comandes_soci')

        # Deleting model 'Proveidor'
        db.delete_table(u'comandes_proveidor')

        # Deleting model 'Producte'
        db.delete_table(u'comandes_producte')

        # Deleting model 'Comanda'
        db.delete_table(u'comandes_comanda')

        # Deleting model 'DetallComanda'
        db.delete_table(u'comandes_detallcomanda')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'comandes.comanda': {
            'Meta': {'object_name': 'Comanda'},
            'data_creacio': ('django.db.models.fields.DateTimeField', [], {}),
            'data_recollida': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preu_rebut': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '5', 'decimal_places': '2'}),
            'soci': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['comandes.Soci']"})
        },
        u'comandes.detallcomanda': {
            'Meta': {'object_name': 'DetallComanda'},
            'comanda': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['comandes.Comanda']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preu_rebut': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '5', 'decimal_places': '2'}),
            'producte': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['comandes.Producte']"}),
            'quantitat': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'quantitat_rebuda': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        u'comandes.globalconf': {
            'Meta': {'object_name': 'GlobalConf'},
            'dow_recollida': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'dow_tancament': ('django.db.models.fields.IntegerField', [], {'default': '4'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_setmanes_previsio': ('django.db.models.fields.IntegerField', [], {'default': '4'})
        },
        u'comandes.producte': {
            'Meta': {'object_name': 'Producte'},
            'granel': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'preu': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '5', 'decimal_places': '2'}),
            'proveidor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['comandes.Proveidor']"}),
            'stock': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'comandes.proveidor': {
            'Meta': {'object_name': 'Proveidor'},
            'cif': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'cp': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'direccio': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'poblacio': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'telefon1': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'telefon2': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'}),
            'telefon3': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'})
        },
        u'comandes.soci': {
            'Meta': {'object_name': 'Soci'},
            'cp': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'direccio': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'dni': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_caixa': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'poblacio': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'telefon1': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'telefon2': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'}),
            'telefon3': ('django.db.models.fields.CharField', [], {'max_length': '9', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['comandes']