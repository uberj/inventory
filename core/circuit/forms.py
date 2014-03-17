from django import forms

from core.circuit.models import Circuit
from core.link.models import Link


class CircuitForm(forms.ModelForm):
    links = forms.ModelMultipleChoiceField(queryset=Link.objects.all())
    links.widget.attrs['class'] = 'core-choose-long'

    class Meta:
        model = Circuit
