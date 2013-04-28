from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.api import Api

from core.group.models import Group


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
