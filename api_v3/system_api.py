from django.conf.urls.defaults import url
from django.core.serializers import json as djson

from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.resources import ModelResource
from tastypie.resources import ALL, ALL_WITH_RELATIONS
from tastypie.serializers import Serializer
from tastypie.authorization import Authorization

import systems.models as system_model
from core.registration.static.models import StaticReg

import json


class PrettyJSONSerializer(Serializer):
    json_indent = 2

    def to_json(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
        return json.dumps(data, cls=djson.DjangoJSONEncoder,
                sort_keys=True, ensure_ascii=False, indent=self.json_indent)

class CustomAPIResource(ModelResource):
    def __init__(self, *args, **kwargs):
        super(CustomAPIResource, self).__init__(*args, **kwargs)

    def determine_format(self, request):
        format = request.GET.get('format')
        if format:
            return super(CustomAPIResource, self).determine_format(request)
        else:
            return "application/json"

    class Meta:
        serializer = PrettyJSONSerializer()
        authorization= Authorization()
        authentication = Authentication()
        allowed_methods = ['get', 'post', 'put', 'delete', 'patch', 'PATCH']

class SystemResource(CustomAPIResource):
    key_value = fields.ToManyField('api_v3.system_api.KeyValueResource', 'keyvalue_set', full=True, null=True)
    server_model = fields.ForeignKey('api_v3.system_api.ServerModelResource', 'server_model', null=True, full=True)
    system_status = fields.ForeignKey('api_v3.system_api.SystemStatusResource', 'system_status', null=True, full=True)
    operating_system = fields.ForeignKey('api_v3.system_api.OperatingSystemResource', 'operating_system', null=True, full=True)
    system_rack = fields.ForeignKey('api_v3.system_api.SystemRackResource', 'system_rack', null=True, full=True)
    allocation = fields.ForeignKey('api_v3.system_api.AllocationResource', 'allocation', null=True, full=True)
    """
        Do not enable the following. It will fail due to the m2m validation routine written by uberj.
        Instead I'm overriding full_dehydrate to get the attributes that we want
        interface = fields.ToManyField('api_v3.system_api.StaticRegResource', 'staticreg_set', null=True, full=True)
    """

    def __init__(self, *args, **kwargs):
        super(SystemResource, self).__init__(*args, **kwargs)

    def prepend_urls(self):
            return [
                url(r"^(?P<resource_name>%s)/(?P<id>[\d]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_system_dispatch_by_id_detail"),
                url(r"^(?P<resource_name>%s)/(?P<hostname>[^schema].*)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_system_dispatch_by_hostname_detail"),
            ]

    class Meta(CustomAPIResource.Meta):
        filtering = {
            'hostname': ALL_WITH_RELATIONS,
            'system_rack': ALL_WITH_RELATIONS,
            'system_status': ALL_WITH_RELATIONS,
            'notes': ALL,
            'asset_tag': ALL,
            'key_value': ALL_WITH_RELATIONS,
            'allocation': ALL_WITH_RELATIONS,
            'key_value__key': ALL_WITH_RELATIONS,
        }
        fields = []
        exclude = ['key_value__system']
        resource_name = 'system'
        queryset = system_model.System.objects.all()

class ServerModelResource(CustomAPIResource):
    class Meta(CustomAPIResource.Meta):
        filtering = {
            'name': ALL,
            'vendor': ALL,
            'model': ALL
        }
        serializer = PrettyJSONSerializer()
        resource_name = 'server_model'
        queryset = system_model.ServerModel.objects.all()

class AllocationResource(CustomAPIResource):
    class Meta(CustomAPIResource.Meta):
        filtering = {
            'name': ALL,
        }
        resource_name = 'allocation'
        queryset = system_model.Allocation.objects.all()

class LocationResource(CustomAPIResource):
    class Meta(CustomAPIResource.Meta):
        resource_name = 'location'
        queryset = system_model.Location.objects.all()

class SystemRackResource(CustomAPIResource):
    class Meta(CustomAPIResource.Meta):
        resource_name = 'system_rack'
        queryset = system_model.SystemRack.objects.all()

        filtering = {
                'name': ALL_WITH_RELATIONS,
                'id': ALL_WITH_RELATIONS,
                }

class AdvisoryDataResource(CustomAPIResource):
    class Meta(CustomAPIResource.Meta):
        resource_name = 'advisory_data'
        queryset = system_model.AdvisoryData.objects.all()
        filtering = {
                'ip_address': ALL_WITH_RELATIONS,
                'title': ALL_WITH_RELATIONS,
                'severity': ALL_WITH_RELATIONS,
                'references': ALL_WITH_RELATIONS,
                'advisory': ALL_WITH_RELATIONS,
                }

class PortDataResource(CustomAPIResource):
    class Meta(CustomAPIResource.Meta):
        resource_name = 'port_data'
        queryset = system_model.PortData.objects.all()
        filtering = {
                'ip_address': ALL_WITH_RELATIONS,
                'state': ALL_WITH_RELATIONS,
                'service': ALL_WITH_RELATIONS,
                'port': ALL_WITH_RELATIONS,
                }

class SystemStatusResource(CustomAPIResource):
    class Meta(CustomAPIResource.Meta):
        resource_name = 'system_status'
        queryset = system_model.SystemStatus.objects.all()
        filtering = {
                'status': ALL_WITH_RELATIONS,
                }


class StaticRegResource(CustomAPIResource):
       
    system = fields.ToOneField(SystemResource, 'system', full=True)
    #system = fields.ForeignKey(SystemResource, 'system', full=True)
    def __init__(self, *args, **kwargs):
        super(StaticRegResource, self).__init__(*args, **kwargs)

    def full_dehydrate(self, bundle):
        super(StaticRegResource, self).full_dehydrate(bundle)
        bundle.obj.update_attrs()
        bundle.data['interface'] = "%s%s.%s" %\
        (bundle.obj.attrs.interface_type,
            bundle.obj.attrs.primary, bundle.obj.attrs.alias)
        del bundle.data['ip_lower']
        del bundle.data['ip_upper']
        del bundle.data['resource_uri']
        return bundle

    class Meta(CustomAPIResource.Meta):
        resource_name = 'interface'
        queryset = StaticReg.objects.select_related().all()

class OperatingSystemResource(CustomAPIResource):
        
    class Meta(CustomAPIResource.Meta):
        resource_name = 'operating_system'
        queryset = system_model.OperatingSystem.objects.all()
        filtering = {
                'version': ALL_WITH_RELATIONS,
                'name': ALL_WITH_RELATIONS,
                }

class OperatingSystemData(CustomAPIResource):
    resource = "operating_system"

    def get_data(self, data):
        data.set('id', '8')
        data.set('name', 'RHEL')
        data.set('resource_uri', '/tasty/v3/operating_system/8/')
        data.set('version', '6.2')
        return data
class KeyValueResource(CustomAPIResource):
    system = fields.ToOneField('api_v3.system_api.SystemResource', 'system', full=False)

    class Meta(CustomAPIResource.Meta):
        filtering = {
                'system': ALL_WITH_RELATIONS,
                'key': ALL_WITH_RELATIONS,
                'value': ALL_WITH_RELATIONS,
                }
        resource_name = 'key_value'
        queryset = system_model.KeyValue.objects.all()
