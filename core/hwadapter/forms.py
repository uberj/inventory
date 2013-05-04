from django import forms

from core.hwadapter.models import HardwareAdapter


class HWAdapterForm(forms.ModelForm):
    class Meta:
        model = HardwareAdapter
