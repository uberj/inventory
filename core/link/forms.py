from django import forms

from core.link.models import Link
from core.circuit.models import Circuit


class LinkForm(forms.ModelForm):
    circuits = forms.ModelMultipleChoiceField(queryset=Circuit.objects.all())
    circuits.widget.attrs['class'] = 'core-choose-long'

    def __init__(self, *args, **kwargs):
        super(LinkForm, self).__init__(*args, **kwargs)
        for attr in ('network', 'a_site', 'z_site'):
            self.fields[attr].widget.attrs['class'] = 'core-choose'

    def save(self, *args, **kwargs):
        super(LinkForm, self).save(*args, **kwargs)
        for c in self.cleaned_data['circuits']:
            c.links.add(self.instance)
            c.save()

    class Meta:
        model = Link
