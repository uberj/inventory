# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ZXTM'
        db.create_table('zxtm_zxtm', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
        ))
        db.send_create_signal('zxtm', ['ZXTM'])

        # Adding field 'Node.zxmt'
        db.add_column('zxtm_node', 'zxmt',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True),
                      keep_default=False)

        # Adding field 'Pool.zxmt'
        db.add_column('zxtm_pool', 'zxmt',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True),
                      keep_default=False)

        # Adding field 'TIG.zxmt'
        db.add_column('zxtm_tig', 'zxmt',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True),
                      keep_default=False)

        # Adding field 'VServer.zxmt'
        db.add_column('zxtm_vserver', 'zxmt',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True),
                      keep_default=False)

        # Adding field 'VServerListenOnTig.zxmt'
        db.add_column('zxtm_vserverlistenontig', 'zxmt',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'ZXTM'
        db.delete_table('zxtm_zxtm')

        # Deleting field 'Node.zxmt'
        db.delete_column('zxtm_node', 'zxmt')

        # Deleting field 'Pool.zxmt'
        db.delete_column('zxtm_pool', 'zxmt')

        # Deleting field 'TIG.zxmt'
        db.delete_column('zxtm_tig', 'zxmt')

        # Deleting field 'VServer.zxmt'
        db.delete_column('zxtm_vserver', 'zxmt')

        # Deleting field 'VServerListenOnTig.zxmt'
        db.delete_column('zxtm_vserverlistenontig', 'zxmt')


    models = {
        'zxtm.node': {
            'Meta': {'object_name': 'Node'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'node_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'pool': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'zxmt': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        'zxtm.pool': {
            'Meta': {'object_name': 'Pool'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'zxmt': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        'zxtm.tig': {
            'Meta': {'object_name': 'TIG'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'zxmt': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        'zxtm.vserver': {
            'Meta': {'object_name': 'VServer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'pool': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'zxmt': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        'zxtm.vserverlistenontig': {
            'Meta': {'object_name': 'VServerListenOnTig'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tig': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'vserver': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'zxmt': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        'zxtm.zxtm': {
            'Meta': {'object_name': 'ZXTM'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        }
    }

    complete_apps = ['zxtm']