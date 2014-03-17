# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Circuit'
        db.create_table('circuit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('circuit_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('service', self.gf('django.db.models.fields.CharField')(default='N/A', max_length=3)),
            ('service_order_number', self.gf('django.db.models.fields.CharField')(default='N/A', max_length=255)),
            ('bandwidth', self.gf('django.db.models.fields.CharField')(default='N/A', max_length=255)),
            ('port_size', self.gf('django.db.models.fields.CharField')(default='N/A', max_length=255)),
            ('price', self.gf('django.db.models.fields.CharField')(default='N/A', max_length=255)),
            ('expiration_date', self.gf('django.db.models.fields.DateField')()),
            ('purchase_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('circuit', ['Circuit'])

        # Adding unique constraint on 'Circuit', fields ['circuit_id']
        db.create_unique('circuit', ['circuit_id'])

        # Adding M2M table for field links on 'Circuit'
        m2m_table_name = db.shorten_name('circuit_links')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('circuit', models.ForeignKey(orm['circuit.circuit'], null=False)),
            ('link', models.ForeignKey(orm['link.link'], null=False))
        ))
        db.create_unique(m2m_table_name, ['circuit_id', 'link_id'])

        # Adding model 'CircuitKeyValue'
        db.create_table('circuit_key_value', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('obj', self.gf('django.db.models.fields.related.ForeignKey')(related_name='keyvalue_set', to=orm['circuit.Circuit'])),
        ))
        db.send_create_signal('circuit', ['CircuitKeyValue'])

        # Adding unique constraint on 'CircuitKeyValue', fields ['key', 'value', 'obj']
        db.create_unique('circuit_key_value', ['key', 'value', 'obj_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'CircuitKeyValue', fields ['key', 'value', 'obj']
        db.delete_unique('circuit_key_value', ['key', 'value', 'obj_id'])

        # Removing unique constraint on 'Circuit', fields ['circuit_id']
        db.delete_unique('circuit', ['circuit_id'])

        # Deleting model 'Circuit'
        db.delete_table('circuit')

        # Removing M2M table for field links on 'Circuit'
        db.delete_table(db.shorten_name('circuit_links'))

        # Deleting model 'CircuitKeyValue'
        db.delete_table('circuit_key_value')


    models = {
        'circuit.circuit': {
            'Meta': {'unique_together': "(('circuit_id',),)", 'object_name': 'Circuit', 'db_table': "'circuit'"},
            'bandwidth': ('django.db.models.fields.CharField', [], {'default': "'N/A'", 'max_length': '255'}),
            'circuit_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'expiration_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'links': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['link.Link']", 'symmetrical': 'False'}),
            'port_size': ('django.db.models.fields.CharField', [], {'default': "'N/A'", 'max_length': '255'}),
            'price': ('django.db.models.fields.CharField', [], {'default': "'N/A'", 'max_length': '255'}),
            'purchase_date': ('django.db.models.fields.DateField', [], {}),
            'service': ('django.db.models.fields.CharField', [], {'default': "'N/A'", 'max_length': '3'}),
            'service_order_number': ('django.db.models.fields.CharField', [], {'default': "'N/A'", 'max_length': '255'})
        },
        'circuit.circuitkeyvalue': {
            'Meta': {'unique_together': "(('key', 'value', 'obj'),)", 'object_name': 'CircuitKeyValue', 'db_table': "'circuit_key_value'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'obj': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'keyvalue_set'", 'to': "orm['circuit.Circuit']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'link.link': {
            'Meta': {'unique_together': "(('a_site', 'z_site', 'network'),)", 'object_name': 'Link', 'db_table': "'link'"},
            'a_site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'a_link_set'", 'to': "orm['site.Site']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['network.Network']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'z_site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'z_link_set'", 'to': "orm['site.Site']"})
        },
        'network.network': {
            'Meta': {'unique_together': "(('ip_upper', 'ip_lower', 'prefixlen'),)", 'object_name': 'Network', 'db_table': "'network'"},
            'dhcpd_raw_include': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_lower': ('django.db.models.fields.BigIntegerField', [], {'blank': 'True'}),
            'ip_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'ip_upper': ('django.db.models.fields.BigIntegerField', [], {'blank': 'True'}),
            'is_reserved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'network_str': ('django.db.models.fields.CharField', [], {'max_length': '49'}),
            'prefixlen': ('django.db.models.fields.PositiveIntegerField', [], {'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['site.Site']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'vlan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vlan.Vlan']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'site.site': {
            'Meta': {'unique_together': "(('full_name',),)", 'object_name': 'Site', 'db_table': "'site'"},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['site.Site']", 'null': 'True', 'blank': 'True'})
        },
        'vlan.vlan': {
            'Meta': {'unique_together': "(('name', 'number'),)", 'object_name': 'Vlan', 'db_table': "'vlan'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['circuit']