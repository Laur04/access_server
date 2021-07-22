from django import forms
from django.forms import ModelForm

from .models import Action, FirewallDevice


class RunForm(forms.Form):
    firewall_device = forms.ModelChoiceField(queryset=FirewallDevice.objects.filter(active=True), required=True)
    action = forms.ModelChoiceField(queryset=Action.objects.all(), required=True)

class ActionCreationForm(ModelForm):
    class Meta:
        model = Action
        fields = [
            'name',
            'script',
        ]

class FirewallDeviceCreationForm(ModelForm):
    class Meta:
        model = FirewallDevice
        fields = [
            'name',
            'hostname',
            'active',
            'notes',
        ]
