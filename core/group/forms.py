from django import forms

from core.vlan.models import Vlan


class VlanForm(forms.ModelForm):
    # site = forms.ModelChoiceField(queryset=Site.objects.all())

    class Meta:
        model = Vlan
