from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.api import Api
from tastypie import fields

from core.group.models import Group
from core.hwadapter.models import HardwareAdapter
from core.registration.static_reg.models import StaticReg

from mozdns.api.v1.api import StaticRegResource


allowed_methods = ['get', 'post', 'patch', 'delete']
v1_core_api = Api(api_name="v1_core")


class GroupResource(ModelResource):
    class Meta:
        always_return_data = True
        queryset = Group.objects.all()
        fields = Group.get_api_fields()
        authorization = Authorization()
        allowed_methods = ['get']
        # This model should be RO, update it in the UI


v1_core_api.register(GroupResource())


class HWAdapterResource(ModelResource):
    sreg = fields.ForeignKey(StaticRegResource, 'sreg')
    group = fields.ForeignKey(GroupResource, 'group', null=True)

    def hydrate(self, bundle):
        # Do everything possible to find an sreg
        possible_pk = bundle.data['sreg']
        if isinstance(possible_pk, int) or possible_pk.isdigit():
            try:
                bundle.data['sreg'] = StaticReg.objects.get(
                    pk=bundle.data['sreg']
                )
            except StaticReg.DoesNotExist:
                pass
        return bundle

    class Meta:
        always_return_data = True
        queryset = HardwareAdapter.objects.all()
        fields = HardwareAdapter.get_api_fields() + ['sreg', 'group']
        authorization = Authorization()
        allowed_methods = ['get', 'post', 'patch', 'delete']


v1_core_api.register(HWAdapterResource())
