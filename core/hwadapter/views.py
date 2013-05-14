from django.http import HttpResponse

from core.hwadapter.forms import HWAdapterForm

import simplejson as json

def ajax_hw_adapter_create(request):
    if not request.POST:
        return HttpResponse('Hi')
    form = HWAdapterForm(request.POST, prefix='add-hw')
    if form.is_valid():
        form.save()
        return HttpResponse(json.dumps({'success': True}))
    return HttpResponse(json.dumps({
        'success': False,
        'form': str(form.as_p())
    }))
