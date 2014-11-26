from django.shortcuts import render
from django.http import HttpResponse

from slurpee.zxtm.utils import fqdn_ip_to_ids

from slurpee.zxtm.models import Node


def zxtm_info(request):
    ident = request.GET.get('ident', '').strip()
    if not ident:
        return HttpResponse()

    return render(request, 'zxtm/zxtm_info.html', {
        'nodes': Node.objects.filter(node_id=ident)
    })
