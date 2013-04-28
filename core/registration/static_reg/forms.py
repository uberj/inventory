from django import forms

from core.registration.static_reg.models import StaticReg
from mozdns.forms import BaseForm


class StaticRegForm(BaseForm):
    class Meta:
        model = StaticReg
        fields = (
            'label', 'domain', 'ip_str', 'ip_type', 'ttl', 'views', 'system',
            'description'
        )
        widgets = {'views': forms.CheckboxSelectMultiple}


class StaticRegFQDNForm(BaseForm):
    class Meta:
        model = StaticReg
        fields = (
            'fqdn', 'ip_str', 'ip_type', 'ttl', 'views', 'description'
        )
        widgets = {'views': forms.CheckboxSelectMultiple}
