from django.conf.urls.defaults import patterns, url, include
from slurpee.views import show_conflicts

urlpatterns = patterns(
    '',
    url(r'^conflicts/', show_conflicts, name='conflicts'),
    url(r'^zxtm/', include('slurpee.zxtm.urls')),
)
