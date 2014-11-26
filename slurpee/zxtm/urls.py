from django.conf.urls.defaults import patterns, url
from slurpee.zxtm.views import zxtm_info

urlpatterns = patterns(
    '',
    url(r'^zxtm_info/', zxtm_info),
)
