from django.shortcuts import get_object_or_404
from django.shortcuts import render

from core.link.models import Circuit, Link
from core.link.forms import CircuitForm, LinkForm
from core.views import CoreDeleteView, CoreListView
from core.views import CoreCreateView, CoreUpdateView

from itertools import izip_longest


class CircuitView(object):
    model = Circuit
    queryset = Circuit.objects.all().order_by('circuit_id')
    form_class = CircuitForm


class CircuitDeleteView(CircuitView, CoreDeleteView):
    success_url = '/core/circuit/'


class CircuitListView(CircuitView, CoreListView):
    pass


class CircuitCreateView(CircuitView, CoreCreateView):
    pass


class CircuitUpdateView(CircuitView, CoreUpdateView):
    pass


class LinkView(object):
    model = Link
    queryset = Circuit.objects.all().order_by('circuit_id')
    form_class = LinkForm


class LinkCreateView(LinkView, CoreCreateView):
    pass


class LinkUpdateView(LinkView, CoreUpdateView):
    pass


def circuit_detail(request, circuit_pk):
    circuit = get_object_or_404(Circuit, pk=circuit_pk)

    a_nets = circuit.a_site.get_allocated_networks()
    z_nets = circuit.z_site.get_allocated_networks()

    return render(request, 'circuit/circuit_detail.html', {
        'circuit': circuit,
        'attrs': circuit.keyvalue_set.all(),
        'site_networks': izip_longest(a_nets, z_nets, fillvalue=None)
    })
