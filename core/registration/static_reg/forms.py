from django import forms

from core.registration.static_reg.models import StaticReg
from mozdns.forms import BaseForm
from mozdns.view.models import View


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

class StaticRegAutoForm(forms.Form):
    sreg_ip_address = forms.CharField()
    sreg_fqdn = forms.CharField()
    sreg_name = forms.CharField()
    sreg_description = forms.CharField()
    sreg_views = forms.ModelChoiceField(
        queryset=View.objects.all(), widget=forms.CheckboxSelectMultiple,
        empty_label=None
    )
