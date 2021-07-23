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
    vlan_number = forms.IntegerField(required=True)
    subnet = forms.CharField(required=True, help_text="In CIDR form please, for example 100.100.100.0/29")

    field_order = ['name', 'subnet', 'vlan_number', 'active', 'notes']
    class Meta:
        model = FirewallDevice
        fields = [
            'name',
            'active',
            'notes',
        ]
