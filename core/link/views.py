from django.shortcuts import get_object_or_404
from django.shortcuts import render

from core.link.models import Link
from core.link.forms import LinkForm
from core.views import CoreDeleteView, CoreListView
from core.views import CoreCreateView, CoreUpdateView

from itertools import izip_longest


class LinkView(object):
    model = Link
    queryset = Link.objects.all()
    form_class = LinkForm


class LinkDeleteView(LinkView, CoreDeleteView):
    success_url = '/core/link/'


class LinkListView(LinkView, CoreListView):
    pass


class LinkCreateView(LinkView, CoreCreateView):
    pass


class LinkUpdateView(LinkView, CoreUpdateView):
    pass


def link_detail(request, pk):
    link = get_object_or_404(Link, pk=pk)

    a_nets = link.a_site.get_allocated_networks()
    z_nets = link.z_site.get_allocated_networks()

    return render(request, 'link/link_detail.html', {
        'link': link,
        'attrs': link.keyvalue_set.all(),
        'site_networks': izip_longest(a_nets, z_nets, fillvalue=None)
    })
