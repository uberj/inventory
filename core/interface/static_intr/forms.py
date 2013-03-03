from django import forms

from core.interface.static_intr.models import StaticInterface
from mozdns.forms import BaseForm


class StaticInterfaceForm(BaseForm):
    class Meta:
        model = StaticInterface
        fields = ('label', 'domain', 'ip_str', 'ip_type', 'ttl', 'views', 'mac',
                   'system', 'description')
        widgets = {'views': forms.CheckboxSelectMultiple}

class StaticInterfaceFQDNForm(BaseForm):
    class Meta:
        model = StaticInterface
        fields = ('fqdn', 'ip_str', 'ip_type', 'ttl', 'views', 'mac',
                   'description')
        widgets = {'views': forms.CheckboxSelectMultiple}
