from django import forms

from core.circuit.models import Circuit, Link


class CircuitForm(forms.ModelForm):
    full_name = forms.CharField()

    class Meta:
        model = Circuit


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
