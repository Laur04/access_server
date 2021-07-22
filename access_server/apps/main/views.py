from ansible_playbook_runner import Runner
from contextlib import redirect_stdout
from io import StringIO
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
            hostname = form.cleaned_data['firewall_device'].hostname
            with open(str(settings.MEDIA_ROOT) + '/hosts', 'w') as host_file:
                host_file.write('[{}]\n{}  ansible_ssh_pass={}\n'.format(hostname, hostname, settings.ANSIBLE_SSH_PASS))
            os.environ['ACTION_HOST'] = hostname

            output = StringIO()
            with redirect_stdout(output):
                exec("Runner(['{}'], '{}').run()".format(str(settings.MEDIA_ROOT) + '/hosts', form.cleaned_data['action'].script.path))
            output = output.getvalue()
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
