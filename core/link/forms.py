from django import forms

from core.link.models import Link


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
