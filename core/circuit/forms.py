from django import forms

from core.circuit.models import Circuit


class CircuitForm(forms.ModelForm):
    full_name = forms.CharField()

    class Meta:
        model = Circuit
