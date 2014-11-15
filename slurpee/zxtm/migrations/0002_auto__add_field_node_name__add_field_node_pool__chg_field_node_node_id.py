# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Node.name'
        db.add_column('zxtm_node', 'name',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True),
                      keep_default=False)

        # Adding field 'Node.pool'
        db.add_column('zxtm_node', 'pool',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True),
                      keep_default=False)


        # Changing field 'Node.node_id'
        db.alter_column('zxtm_node', 'node_id', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Pool.name'
        db.alter_column('zxtm_pool', 'name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'TIG.name'
        db.alter_column('zxtm_tig', 'name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'VServer.pool'
        db.alter_column('zxtm_vserver', 'pool', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'VServer.name'
        db.alter_column('zxtm_vserver', 'name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'VServerListenOnTig.vserver'
        db.alter_column('zxtm_vserverlistenontig', 'vserver', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'VServerListenOnTig.tig'
        db.alter_column('zxtm_vserverlistenontig', 'tig', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

    def backwards(self, orm):
        # Deleting field 'Node.name'
        db.delete_column('zxtm_node', 'name')

        # Deleting field 'Node.pool'
        db.delete_column('zxtm_node', 'pool')


        # User chose to not deal with backwards NULL issues for 'Node.node_id'
        raise RuntimeError("Cannot reverse this migration. 'Node.node_id' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Node.node_id'
        db.alter_column('zxtm_node', 'node_id', self.gf('django.db.models.fields.CharField')(max_length=255))

        # User chose to not deal with backwards NULL issues for 'Pool.name'
        raise RuntimeError("Cannot reverse this migration. 'Pool.name' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Pool.name'
        db.alter_column('zxtm_pool', 'name', self.gf('django.db.models.fields.CharField')(max_length=255))

        # User chose to not deal with backwards NULL issues for 'TIG.name'
        raise RuntimeError("Cannot reverse this migration. 'TIG.name' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'TIG.name'
        db.alter_column('zxtm_tig', 'name', self.gf('django.db.models.fields.CharField')(max_length=255))

        # User chose to not deal with backwards NULL issues for 'VServer.pool'
        raise RuntimeError("Cannot reverse this migration. 'VServer.pool' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'VServer.pool'
        db.alter_column('zxtm_vserver', 'pool', self.gf('django.db.models.fields.CharField')(max_length=255))

        # User chose to not deal with backwards NULL issues for 'VServer.name'
        raise RuntimeError("Cannot reverse this migration. 'VServer.name' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'VServer.name'
        db.alter_column('zxtm_vserver', 'name', self.gf('django.db.models.fields.CharField')(max_length=255))

        # User chose to not deal with backwards NULL issues for 'VServerListenOnTig.vserver'
        raise RuntimeError("Cannot reverse this migration. 'VServerListenOnTig.vserver' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'VServerListenOnTig.vserver'
        db.alter_column('zxtm_vserverlistenontig', 'vserver', self.gf('django.db.models.fields.CharField')(max_length=255))

        # User chose to not deal with backwards NULL issues for 'VServerListenOnTig.tig'
        raise RuntimeError("Cannot reverse this migration. 'VServerListenOnTig.tig' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'VServerListenOnTig.tig'
        db.alter_column('zxtm_vserverlistenontig', 'tig', self.gf('django.db.models.fields.CharField')(max_length=255))

    models = {
        'zxtm.node': {
            'Meta': {'object_name': 'Node'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'node_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'pool': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        'zxtm.pool': {
            'Meta': {'object_name': 'Pool'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        'zxtm.tig': {
            'Meta': {'object_name': 'TIG'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        'zxtm.vserver': {
            'Meta': {'object_name': 'VServer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'pool': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        'zxtm.vserverlistenontig': {
            'Meta': {'object_name': 'VServerListenOnTig'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tig': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'vserver': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        }
    }

    complete_apps = ['zxtm']