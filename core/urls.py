from django.conf.urls.defaults import patterns, url, include

from django.views.decorators.csrf import csrf_exempt

from core.search.views import search


urlpatterns = patterns('',
                       url(r'^$', csrf_exempt(search), name='core-index'),
                       url(r'^interface/', include('core.interface.urls')),
                       url(r'^vlan/', include('core.vlan.urls')),
                       url(r'^network/', include('core.network.urls')),
                       url(r'^site/', include('core.site.urls')),
                       url(r'^range/', include('core.range.urls')),
                       url(r'^build/', include('core.build.urls')),
                       url(r'^search/', include('core.search.urls')),
                       url(r'^keyvalue/', include('core.keyvalue.urls')),
                       )
