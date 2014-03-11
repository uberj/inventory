from django.conf.urls.defaults import patterns, url

from core.circuit.views import *  # noqa

urlpatterns = patterns(
    '',
    url(r'^$', CircuitListView.as_view(), name='link-list'),

    url(r'^create/$', LinkCreateView.as_view()),
    url(r'^(?P<circuit_pk>[\w-]+)/$', link_detail),
    url(r'^(?P<pk>[\w-]+)/update/$', LinkUpdateView.as_view()),
    url(r'^(?P<pk>[\w-]+)/delete/$', LinkDeleteView.as_view()),
    url(r'^(?P<pk>[\w-]+)/update/$', LinkUpdateView.as_view()),
    url(r'^(?P<pk>[\w-]+)/delete/$', LinkDeleteView.as_view()),

    url(r'^circuit/$', CircuitListView.as_view(), name='circuit-list'),
    url(r'^circuit/create/$', CircuitCreateView.as_view()),
    url(r'^circuit/(?P<circuit_pk>[\w-]+)/$', circuit_detail),
    url(r'^circuit/(?P<pk>[\w-]+)/update/$', CircuitUpdateView.as_view()),
    url(r'^circuit/(?P<pk>[\w-]+)/delete/$', CircuitDeleteView.as_view()),
    url(r'^circuit/(?P<pk>[\w-]+)/update/$', CircuitUpdateView.as_view()),
    url(r'^circuit/(?P<pk>[\w-]+)/delete/$', CircuitDeleteView.as_view()),
)
