from django import forms
from django.forms import ModelForm

from .models import Action, FirewallDevice, ScheduledTask


class RunForm(forms.Form):
    firewall_devices = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=FirewallDevice.objects.filter(active=True), required=True)
    actions = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Action.objects.all(), required=True)

class ScheduleRunForm(ModelForm):
    class Meta:
        model = ScheduledTask
        fields = [
            'name',
            'devices',
            'actions',
            'time_to_run',
        ]
        widgets = {
            'devices': forms.CheckboxSelectMultiple,
            'actions': forms.CheckboxSelectMultiple,
            'time_to_run': forms.TimeInput,
        }
        labels = {
            'time_to_run': "Time to run (24hr time):"
        }

class ActionCreationForm(ModelForm):
    content = forms.CharField(max_length=10000, widget=forms.Textarea)

    class Meta:
        model = Action
        fields = [
            'name',
        ]

class FirewallDeviceCreationForm(ModelForm):
    vlan_number = forms.IntegerField(required=True)
    subnet = forms.CharField(required=True, label='Subnet in CIDR form')

    class Meta:
        model = FirewallDevice
        fields = [
            'name',
            'subnet',
            'vlan_number',
            'active',
            'notes',
        ]
        labels = {
            'subnet': "Subnet in CIDR form:"
        }
