from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.forms.formsets import formset_factory
from django.db import transaction, IntegrityError

from core.registration.static.forms import StaticRegAutoForm
from core.hwadapter.forms import HWAdapterForm
import simplejson as json


def ajax_create_sreg(request):
    HWAdapterFormset = formset_factory(HWAdapterForm)

    sreg_form = StaticRegAutoForm(request.POST, prefix='sreg')
    hw_formset = HWAdapterFormset(request.POST, prefix='hwadapters')

    @transaction.commit_on_success
    def save_objects():
        # This really is a pile of hack
        errors = {}
        try:
            if not sreg_form.is_valid():
                errors['sreg'] = sreg_form.errors.items()
                return errors
            sreg = sreg_form.save()
        except ValidationError, e:
            errors['sreg'] = [('__all__', e.messages)]
            return errors

        error_list = []  # Where to keep the errors
        error = False  # Flag if there were errors
        for hwform in hw_formset:
            hwform.initial['sreg'] = sreg
            if hwform.is_valid():
                hwform.instance.sreg = sreg  # WTF, why doesn't initial do this?
                try:
                    hwform.save()
                except IntegrityError, e:
                    # the MySQL driver is such a load of crap
                    if 'Duplicate entry' in str(e):
                        error_list.append(
                            [('', 'This seems to be a duplicate entry')]
                        )
                    error = True
                else:
                    error_list.append([])
            else:
                error = True
                error_list.append(hwform.errors.items())

        if error:
            transaction.rollback()
            errors['hw_adapters'] = error_list

        return errors

    errors = save_objects()

    #if not result:
    if errors:
        return HttpResponse(json.dumps({
            'success': False,
            'errors': errors
        }))
    return HttpResponse(json.dumps({
        'success': True
    }))
