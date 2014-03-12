from django.shortcuts import get_object_or_404
from django.shortcuts import render

from core.link.models import Circuit
from core.link.forms import CircuitForm
from core.views import CoreDeleteView, CoreListView
from core.views import CoreCreateView, CoreUpdateView


class CircuitView(object):
    model = Circuit
    queryset = Circuit.objects.all().order_by('circuit_id')
    form_class = CircuitForm


class CircuitDeleteView(CircuitView, CoreDeleteView):
    success_url = '/core/link/'


class CircuitListView(CircuitView, CoreListView):
    pass


class CircuitCreateView(CircuitView, CoreCreateView):
    pass


class CircuitUpdateView(CircuitView, CoreUpdateView):
    pass


def circuit_detail(request, pk):
    circuit = get_object_or_404(Circuit, pk=pk)

    return render(request, 'circuit/circuit_detail.html', {
        'circuit': circuit,
    })
