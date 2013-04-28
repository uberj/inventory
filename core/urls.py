from django.conf.urls.defaults import patterns, url, include

from django.views.decorators.csrf import csrf_exempt

from core.search.views import search
from core.api.v1.api import v1_core_api


urlpatterns = patterns('',
   url(r'^$', csrf_exempt(search), name='core-index'),
   url(r'^interface/', include('core.interface.urls')),
   url(r'^vlan/', include('core.vlan.urls')),
   url(r'^network/', include('core.network.urls')),
   url(r'^site/', include('core.site.urls')),
   url(r'^range/', include('core.range.urls')),
   url(r'^group/', include('core.group.urls')),
   url(r'^dhcp/', include('core.dhcp.urls')),
   url(r'^search/', include('core.search.urls')),
   url(r'^keyvalue/', include('core.keyvalue.urls')),
   url(r'^api/', include(v1_core_api.urls)),
)
