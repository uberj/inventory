from django.conf.urls.defaults import patterns, url

from core.circuit.views import *  # noqa

urlpatterns = patterns(
    '',
    url(r'^$', CircuitListView.as_view(), name='circuit-list'),
    url(r'^create/$', CircuitCreateView.as_view()),
    url(r'^(?P<pk>[\d-]+)/$', circuit_detail),
    url(r'^(?P<pk>[\d-]+)/update/$', CircuitUpdateView.as_view()),
    url(r'^(?P<pk>[\d-]+)/delete/$', CircuitDeleteView.as_view()),
)
