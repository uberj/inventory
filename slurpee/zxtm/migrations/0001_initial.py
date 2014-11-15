# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Node'
        db.create_table('zxtm_node', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('zxtm', ['Node'])

        # Adding model 'VServer'
        db.create_table('zxtm_vserver', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('pool', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('zxtm', ['VServer'])

        # Adding model 'VServerListenOnTig'
        db.create_table('zxtm_vserverlistenontig', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vserver', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('tig', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('zxtm', ['VServerListenOnTig'])

        # Adding model 'TIG'
        db.create_table('zxtm_tig', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('zxtm', ['TIG'])

        # Adding model 'Pool'
        db.create_table('zxtm_pool', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('zxtm', ['Pool'])


    def backwards(self, orm):
        # Deleting model 'Node'
        db.delete_table('zxtm_node')

        # Deleting model 'VServer'
        db.delete_table('zxtm_vserver')

        # Deleting model 'VServerListenOnTig'
        db.delete_table('zxtm_vserverlistenontig')

        # Deleting model 'TIG'
        db.delete_table('zxtm_tig')

        # Deleting model 'Pool'
        db.delete_table('zxtm_pool')


    models = {
        'zxtm.node': {
            'Meta': {'object_name': 'Node'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node_id': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'zxtm.pool': {
            'Meta': {'object_name': 'Pool'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'zxtm.tig': {
            'Meta': {'object_name': 'TIG'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'zxtm.vserver': {
            'Meta': {'object_name': 'VServer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pool': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'zxtm.vserverlistenontig': {
            'Meta': {'object_name': 'VServerListenOnTig'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tig': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'vserver': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['zxtm']