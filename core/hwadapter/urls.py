from django.conf.urls.defaults import patterns, url

from core.hwadapter.views import ajax_hw_adapter_create

urlpatterns = patterns('',
   url(r'^create/$', ajax_hw_adapter_create),
)
