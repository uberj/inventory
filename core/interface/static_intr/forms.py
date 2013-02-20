from django import forms
from django.core.exceptions import ValidationError

from core.interface.static_intr.models import StaticInterface
from mozdns.view.models import View
from core.range.models import Range
from mozdns.validation import validate_label
from mozdns.forms import BaseForm
from systems.models import System
from core.validation import validate_mac

import ipaddr


def validate_ip(ip):
    try:
        ipaddr.IPv4Address(ip)
    except ipaddr.AddressValueError:
        try:
            ipaddr.IPv6Address(ip)
        except ipaddr.AddressValueError:
            raise ValidationError("IP address not in valid form.")


class CombineForm(forms.Form):
    mac = forms.CharField(validators=[validate_mac])
    system = forms.ModelChoiceField(queryset=System.objects.all())


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


class FullStaticInterfaceForm(BaseForm):
    views = forms.ModelMultipleChoiceField(
        queryset=View.objects.all(),
        widget=forms.widgets.CheckboxSelectMultiple, required=False)

    class Meta:
        model = StaticInterface
        exclude = ('ip_upper', 'ip_lower', 'reverse_domain',
                   'fqdn')

