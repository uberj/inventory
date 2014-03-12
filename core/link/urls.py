from django.conf.urls.defaults import patterns, url

from core.link.views import *  # noqa

urlpatterns = patterns(
    '',
    url(r'^$', LinkListView.as_view(), name='link-list'),

    url(r'^create/$', LinkCreateView.as_view()),
    url(r'^(?P<pk>[\d-]+)/$', link_detail),
    url(r'^(?P<pk>[\d-]+)/update/$', LinkUpdateView.as_view()),
    url(r'^(?P<pk>[\d-]+)/delete/$', LinkDeleteView.as_view()),
)
