# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Cooperativa'
        db.create_table(u'comandes_cooperativa', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nom', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('direccio', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('cp', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('poblacio', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('contacte', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('telefon1', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('telefon2', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('telefon3', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'comandes', ['Cooperativa'])

        # Adding field 'Proveidor.notes'
        db.add_column(u'comandes_proveidor', 'notes',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding M2M table for field cooperatives on 'Proveidor'
        m2m_table_name = db.shorten_name(u'comandes_proveidor_cooperatives')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('proveidor', models.ForeignKey(orm[u'comandes.proveidor'], null=False)),
            ('cooperativa', models.ForeignKey(orm[u'comandes.cooperativa'], null=False))
        ))
        db.create_unique(m2m_table_name, ['proveidor_id', 'cooperativa_id'])


        # Changing field 'Proveidor.telefon3'
        db.alter_column(u'comandes_proveidor', 'telefon3', self.gf('django.db.models.fields.CharField')(max_length=30))

        # Changing field 'Proveidor.telefon1'
        db.alter_column(u'comandes_proveidor', 'telefon1', self.gf('django.db.models.fields.CharField')(max_length=30))

        # Changing field 'Proveidor.telefon2'
        db.alter_column(u'comandes_proveidor', 'telefon2', self.gf('django.db.models.fields.CharField')(max_length=30))
        # Adding field 'Producte.actiu'
        db.add_column(u'comandes_producte', 'actiu',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Producte.notes'
        db.add_column(u'comandes_producte', 'notes',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'GlobalConf.hora_tancament'
        db.add_column(u'comandes_globalconf', 'hora_tancament',
                      self.gf('django.db.models.fields.TimeField')(default=datetime.time(14, 0)),
                      keep_default=False)

        # Adding field 'Soci.cooperativa'
        db.add_column(u'comandes_soci', 'cooperativa',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['comandes.Cooperativa'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Soci.notes'
        db.add_column(u'comandes_soci', 'notes',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Cooperativa'
        db.delete_table(u'comandes_cooperativa')

        # Deleting field 'Proveidor.notes'
        db.delete_column(u'comandes_proveidor', 'notes')

        # Removing M2M table for field cooperatives on 'Proveidor'
        db.delete_table(db.shorten_name(u'comandes_proveidor_cooperatives'))


        # Changing field 'Proveidor.telefon3'
        db.alter_column(u'comandes_proveidor', 'telefon3', self.gf('django.db.models.fields.CharField')(max_length=9))

        # Changing field 'Proveidor.telefon1'
        db.alter_column(u'comandes_proveidor', 'telefon1', self.gf('django.db.models.fields.CharField')(max_length=9))

        # Changing field 'Proveidor.telefon2'
        db.alter_column(u'comandes_proveidor', 'telefon2', self.gf('django.db.models.fields.CharField')(max_length=9))
        # Deleting field 'Producte.actiu'
        db.delete_column(u'comandes_producte', 'actiu')

        # Deleting field 'Producte.notes'
        db.delete_column(u'comandes_producte', 'notes')

        # Deleting field 'GlobalConf.hora_tancament'
        db.delete_column(u'comandes_globalconf', 'hora_tancament')

        # Deleting field 'Soci.cooperativa'
        db.delete_column(u'comandes_soci', 'cooperativa_id')

        # Deleting field 'Soci.notes'
        db.delete_column(u'comandes_soci', 'notes')


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
        u'comandes.cooperativa': {
            'Meta': {'object_name': 'Cooperativa'},
            'contacte': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'cp': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'direccio': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'poblacio': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'telefon1': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'telefon2': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'telefon3': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
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
            'hora_tancament': ('django.db.models.fields.TimeField', [], {'default': 'datetime.time(14, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_setmanes_previsio': ('django.db.models.fields.IntegerField', [], {'default': '4'})
        },
        u'comandes.producte': {
            'Meta': {'object_name': 'Producte'},
            'actiu': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'granel': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'preu': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '5', 'decimal_places': '2'}),
            'proveidor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['comandes.Proveidor']"}),
            'stock': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'comandes.proveidor': {
            'Meta': {'object_name': 'Proveidor'},
            'cif': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'cooperatives': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['comandes.Cooperativa']", 'symmetrical': 'False'}),
            'cp': ('django.db.models.fields.CharField', [], {'max_length': '8', 'blank': 'True'}),
            'direccio': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'poblacio': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'telefon1': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'telefon2': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'telefon3': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        u'comandes.soci': {
            'Meta': {'object_name': 'Soci'},
            'cooperativa': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['comandes.Cooperativa']", 'null': 'True', 'blank': 'True'}),
            'cp': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'direccio': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'dni': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
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