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
    display, error = None, None
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
            print(output)

            try:
                display = {
                    'outcome': 'Success!' if output.count('fatal') == 0 else 'Error',
                    'tasks': [s[2:s.index(']')] for s in output.split('TASK')][2:],
                    'raw': output,
                }
            except:
                error = output
    else:
        form = RunForm()

    return render(request, 'index.html', context={'form': form, 'display': display, 'error': error})

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
            firewall = form.save()
            firewall.hostname = 'internal-node-' + firewall.name.lower().replace(' ', '-')
            firewall.save()
            
            full_address = form.cleaned_data['subnet'].split('/')[0]
            network_address = full_address[:full_address.rindex('.')]
            first_host_address = int(full_address[full_address.rindex('.') + 1:])
            gateway_host_address = str(first_host_address + 1)
            control_node_host_address = str(first_host_address + 2)
            internal_node_host_address = str(first_host_address + 3)

            os.environ['D3_HOSTNAME'] = firewall.hostname.replace(' ', '-')
            os.environ['D3_NETWORK_NAME'] =  'internal-net-' + firewall.name.lower().replace(' ', '-')
            os.environ['D3_NETWORK'] = form.cleaned_data['subnet']
            os.environ['D3_INTERFACE'] = 'ens160.' + str(form.cleaned_data['vlan_number'])
            os.environ['D3_GATEWAY'] = network_address + '.' + gateway_host_address
            os.environ['D3_CONTROL_NODE_IP'] = network_address + '.' + control_node_host_address
            os.environ['D3_CONTAINER_IP'] = network_address + '.' + internal_node_host_address
            
            exec("Runner(['{}'], '{}').run()".format(str(settings.STATIC_ROOT) + '/hosts', str(settings.STATIC_ROOT) + '/spinup.yml'))
            return redirect(reverse('index'))
    else:
        form = FirewallDeviceCreationForm()

    help = """
    This will perform much of the setup. However, for this to work you need to first:
     - create a unique vlan on the lab's Cisco switch
     - pick an available /29 subnet from 100.100.100.0
     - bring up and assign the physical firewall device the first available ip address in that subnet
     - ensure the firewall's port is set as switch mode access <vlan>
    """
    
    return render(request, 'add.html', context={'form': form, 'help': help})

