from django.shortcuts import render
from django.http import HttpResponse

from slurpee.zxtm.models import Node


def zxtm_info(request):
    ident = request.GET.get('ident', '').strip()
    if not ident:
        return HttpResponse('')

    nodes = Node.objects.filter(node_id=ident)

    if not nodes:
        return HttpResponse('')

    return render(request, 'zxtm/zxtm_info.html', {
        'nodes': nodes
    })
