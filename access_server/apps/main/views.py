import os
import subprocess

from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import RunForm, ActionCreationForm, FirewallDeviceCreationForm
from .models import Action, FirewallDevice

def index(request):
    form = None
    output = None
    if request.method == 'POST':
        form = RunForm(request.POST)
        if form.is_valid():
            hostname = FirewallDevice.objects.get(id=form.cleaned_data['firewall_device']).hostname
            with open(settings.MEDIA_ROOT + '/hosts', 'a') as host_file:
                host_file.write('[{}]\n{}  ansible_ssh_pass={}'.format(hostname, hostname, settings.ANSIBLE_SSH_PASS))
            os.environ['ACTION_HOST'] = hostname
            file_path = Action.objects.get(id=form.cleaned_data['action']).script.path
            try:
                output = subprocess.check_output("Runner(['{}'], '{}').run()".format(settings.MEDIA_ROOT + '/hosts', file_path))
            except subprocess.CalledProcessError as err:
                output = err
    else:
        form = RunForm()

    return render(request, 'index.html', context={'form': form, 'output': output})

def add_action(request):
    form = None
    if request.method == 'POST':
        form = ActionCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('index'))
    else:
        form = ActionCreationForm()

    help = """
    The task must be an ansible play in the general form:
    ---
    
    - hosts: "{{ lookup('env', 'ACTION_HOST') }}"
      remote_user: controller
      tasks:
        - name: Connect to Google
          uri:
            url: https://google.com
        
        - name: More tasks!
          ...

    """
    
    return render(request, 'add.html', context={'form': form, 'help': help})

def add_device(request):
    form = None
    if request.method == 'POST':
        form = FirewallDeviceCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('index'))
    else:
        form = FirewallDeviceCreationForm()
    
    return render(request, 'add.html', context={'form': form})
