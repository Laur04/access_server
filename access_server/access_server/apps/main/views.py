from ansible_playbook_runner import Runner
from contextlib import redirect_stdout
from datetime import datetime
from io import StringIO
import os
import random

from django.conf import settings
from django.core.files.base import File
from django.http.response import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse

from .forms import RunForm, ScheduleRunForm, ActionCreationForm, FirewallDeviceCreationForm
from .models import Action, FirewallDevice, ScheduledTask


def index(request):
    form = RunForm()
    return render(request, 'index.html', context={'form': form})

def status(request):
    return render(request, 'status.html', context={'firewalls': FirewallDevice.objects.all()})

def run_status(request, device_id):
    device = get_object_or_404(FirewallDevice, id=device_id)
    statuses = []

    # determine if container is up
    output = StringIO()
    with redirect_stdout(output):
        exec("Runner(['{}'], '{}').run()".format(str(settings.STATIC_ROOT) + '/hosts', str(settings.STATIC_ROOT) + '/status_one.yml'))
    output = output.getvalue()
    result = device.hostname in output
    if result:
        statuses.append("The firewall container is online.")
    else:
        statuses.append("The firewall container is down. ssh into firewall_lab_host and run docker restart to bring it back up.")

    if result:
        # set up status tasks on container
        os.environ['STATUS_HOSTNAME'] = device.hostname
        with open(str(settings.MEDIA_ROOT) + '/hosts', 'w') as host_file:
            host_file.write('[{}]\n{}  ansible_ssh_pass={}\n'.format(device.hostname, device.hostname, settings.ANSIBLE_SSH_PASS))
        full_address = device.subnet.split('/')[0]
        gateway_full_address = full_address[:full_address.rindex('.')] + '.' + str(int(full_address[full_address.rindex('.') + 1:]) + 1)
        os.environ['ADDRESS'] = gateway_full_address

        # determine if associated firewall is up
        output = StringIO()
        with redirect_stdout(output):
            exec("Runner(['{}'], '{}').run()".format(str(settings.MEDIA_ROOT) + '/hosts', str(settings.STATIC_ROOT) + '/status_two.yml'))
        output = output.getvalue()
        result = "64 bytes from" in output
        if result:
            statuses.append("The firewall device is pingable.")
        else:
            statuses.append("The firewall device isn't pingable. Either the firewall container is down (see above) or the device itself is offline.")

        # determine if container default route is set correctly
        output = StringIO()
        with redirect_stdout(output):
            exec("Runner(['{}'], '{}').run()".format(str(settings.MEDIA_ROOT) + '/hosts', str(settings.STATIC_ROOT) + '/status_three.yml'))
        output = output.getvalue()
        result = "default via {}".format(gateway_full_address) in output
        if result:
            statuses.append("The firewall container is routing traffic correctly.")
        else:
            statuses.append("The firewall container isn't routing traffic correctly. Check its default route.")
    else:
        # if the container isn't up, we can't test the other stuff
        statuses.append("The firewall device isn't pingable because the firewall container is down (see above).")
        statuses.append("The firewall container isn't routing traffic correctly because it is down (see above).")

    response = {
        'statuses': statuses,
        'time': datetime.now()
    }

    return JsonResponse(response)

def run_action(request, device_id, action_id):
    if request.is_ajax():
        hostname = FirewallDevice.objects.get(id=int(device_id)).hostname
        action = Action.objects.get(id=int(action_id))

        with open(str(settings.MEDIA_ROOT) + '/hosts', 'w') as host_file:
            host_file.write('[{}]\n{}  ansible_ssh_pass={}\n'.format(hostname, hostname, settings.ANSIBLE_SSH_PASS))
        os.environ['ACTION_HOST'] = hostname
        output = StringIO()
        with redirect_stdout(output):
            exec("Runner(['{}'], '{}').run()".format(str(settings.MEDIA_ROOT) + '/hosts', action.script.path))
        output = output.getvalue()
        print(output)

        try:
            response = {
                'hostname': hostname,
                'action': action.name,
                'outcome': 'Success!' if output.count('fatal') == 0 else 'Error',
                'tasks': [s[2:s.index(']')] for s in output.split('TASK')][2:],
                'raw': output,
            }
        except:
            response = {
                'hostname': hostname,
                'action': action.name,
                'outcome': 'Critical Error',
                'tasks': [],
                'raw': output,
            }

        return JsonResponse(response)                     

def manage_action(request):
    return render(request, 'manage_action.html', context={'items': Action.objects.all()})

def add_action(request):
    default_action_text = """
    ---

    - hosts: "{{ lookup('env', 'ACTION_HOST') }}"
    remote_user: controller
    tasks:
        - name: Verify internet connectivity
        uri:
            url: google.com

        - name: <something descriptive>
        <some ansible module>:
            <options for that module>
    """

    form = None
    if request.method == 'POST':
        form = ActionCreationForm(request.POST, request.FILES)
        if form.is_valid():
            action = form.save()
            filename = form.cleaned_data["name"] + str(random.randrange(1, 10000)) + '.yml'
            with open(filename, 'w+') as f:
                f.write(form.cleaned_data["content"])
                action.script.save(filename, File(f))
            
            return redirect(reverse('manage_action'))
    else:
        form = ActionCreationForm(initial={'content': default_action_text})

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
    
    return render(request, 'add_edit.html', context={'form': form, 'help': help})

def edit_action(request, action_id):
    action = get_object_or_404(Action, id=action_id)

    form = None
    current_script_content = ""
    with open(action.script.path, 'r') as f:
        current_script_content = f.read()
    if request.method == 'POST':
        form = ActionCreationForm(request.POST, request.FILES, instance=action)
        if form.is_valid():
            action = form.save()
            with open(action.script.path, 'w+') as f:
                f.write(form.cleaned_data["content"])
                action.script.save(action.script.name, File(f))

            return redirect(reverse('manage_action'))
    else:
        form = ActionCreationForm(instance=action, initial={'content': current_script_content})

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

    return render(request, 'add_edit.html', context={'form': form, 'help': help})

def delete_action(request, action_id):
    action = get_object_or_404(Action, id=action_id)

    action.delete()

    return redirect(reverse('manage_action'))


def manage_device(request):
    return render(request, 'manage_device.html', context={'items': FirewallDevice.objects.all()})

def add_device(request):
    form = None
    error = None
    if request.method == 'POST':
        form = FirewallDeviceCreationForm(request.POST)
        if form.is_valid():

            hostname = 'internal-node-' + form.cleaned_data['name'].lower().replace(' ', '-')
            full_address = form.cleaned_data['subnet'].split('/')[0]
            network_address = full_address[:full_address.rindex('.')]
            first_host_address = int(full_address[full_address.rindex('.') + 1:])
            gateway_host_address = str(first_host_address + 1)
            internal_node_host_address = str(first_host_address + 2)

            os.environ['D3_HOSTNAME'] = hostname
            os.environ['D3_NETWORK_NAME'] =  'internal-net-' + form.cleaned_data['name'].lower().replace(' ', '-')
            os.environ['D3_NETWORK'] = form.cleaned_data['subnet']
            os.environ['D3_INTERFACE'] = 'ens160.' + str(form.cleaned_data['vlan_number'])
            os.environ['D3_GATEWAY'] = network_address + '.' + gateway_host_address
            os.environ['D3_CONTROL_NET_IP'] = '172.28.0.' + str(form.cleaned_data['vlan_number'])
            os.environ['D3_CONTAINER_IP'] = network_address + '.' + internal_node_host_address
            

            output = StringIO()
            with redirect_stdout(output):
                exec("Runner(['{}'], '{}').run()".format(str(settings.STATIC_ROOT) + '/hosts', str(settings.STATIC_ROOT) + '/spinup.yml'))
            output = output.getvalue()
            print(output)
            successful = True if output.count('fatal') == 0 else False

            if successful:
                firewall = form.save()
                firewall.hostname = hostname
                firewall.save()
                return redirect(reverse('manage_device'))
            else:
                error = output
    else:
        form = FirewallDeviceCreationForm()

    help = """
    Don't use a vlan number less than 10.

    This will perform much of the setup. However, for this to work you need to first:
     - create a unique vlan on the lab's Cisco switch
     - pick an available /29 subnet from 100.100.100.0
     - bring up and assign the physical firewall device the first available ip address in that subnet
     - ensure the firewall's port is set as switch mode access <vlan>
    """
    
    return render(request, 'add_edit.html', context={'form': form, 'error': error, 'help': help})

def edit_device(request, device_id):
    device = get_object_or_404(FirewallDevice, id=device_id)

    form = None
    if request.method == 'POST':
        form = FirewallDeviceCreationForm(request.POST, instance=device)
        if form.is_valid():

            hostname = 'internal-node-' + device.name.lower().replace(' ', '-')
            full_address = form.cleaned_data['subnet'].split('/')[0]
            network_address = full_address[:full_address.rindex('.')]
            first_host_address = int(full_address[full_address.rindex('.') + 1:])
            gateway_host_address = str(first_host_address + 1)
            internal_node_host_address = str(first_host_address + 2)

            os.environ['D3_HOSTNAME'] = hostname
            os.environ['D3_NETWORK_NAME'] =  'internal-net-' + device.name.lower().replace(' ', '-')
            os.environ['D3_NETWORK'] = form.cleaned_data['subnet']
            os.environ['D3_INTERFACE'] = 'ens160.' + str(form.cleaned_data['vlan_number'])
            os.environ['D3_GATEWAY'] = network_address + '.' + gateway_host_address
            os.environ['D3_CONTROL_NET_IP'] = '172.28.0.' + str(form.cleaned_data['vlan_number'])
            os.environ['D3_CONTAINER_IP'] = network_address + '.' + internal_node_host_address
            
            exec("Runner(['{}'], '{}').run()".format(str(settings.STATIC_ROOT) + '/hosts', str(settings.STATIC_ROOT) + '/spinup.yml'))

            firewall = form.save()
            firewall.hostname = hostname
            firewall.save()

            return redirect(reverse('manage_device'))
    else:
        form = FirewallDeviceCreationForm(instance=device)

    help = """
    Don't use a vlan number less than 10.

    This will perform much of the setup. However, for this to work you need to first:
     - create a unique vlan on the lab's Cisco switch
     - pick an available /29 subnet from 100.100.100.0
     - bring up and assign the physical firewall device the first available ip address in that subnet
     - ensure the firewall's port is set as switch mode access <vlan>
    """
    
    return render(request, 'add_edit.html', context={'form': form, 'help': help})

def delete_device(request, device_id):
    device = get_object_or_404(FirewallDevice, id=device_id)

    os.environ['D3_HOSTNAME_TO_RM'] = device.hostname
    exec("Runner(['{}'], '{}').run()".format(str(settings.STATIC_ROOT) + '/hosts', str(settings.STATIC_ROOT) + '/spindown.yml'))
    device.delete()

    return redirect(reverse('manage_device'))

def manage_task(request):
    return render(request, 'manage_task.html', context={'items': ScheduledTask.objects.all()})

def add_task(request):
    form = None
    if request.method == 'POST':
        form = ScheduleRunForm(request.POST)
        if form.is_valid():
            st = form.save()
            with open('/etc/periodic/access-server' + str(st.id), 'w+') as file:
                file.write('{} {} {} {} {} python3 manage.py run_scheduled_task {}\n\n'.format(st.minute, st.hour, st.day_of_month, st.month, st.day_of_week, st.id))
            os.chmod('/etc/periodic/access-server' + str(st.id), 0o777)
            cmd = 'crond -c /etc/periodic/access-server' + str(st.id)
            os.system(cmd)

            return redirect(reverse('manage_task'))
    else:
        form = ScheduleRunForm()

    help = """
    This will add a cron job to run this task at a specified time each day.
    """
    
    return render(request, 'add_edit.html', context={'form': form, 'help': help})

def edit_task(request, task_id):
    task = get_object_or_404(ScheduledTask, id=task_id)

    form = None
    if request.method == 'POST':
        form = ScheduleRunForm(request.POST, instance=task)
        if form.is_valid():
            st = form.save()
            with open('/etc/periodic/access-server' + str(st.id), 'w+') as file:
                file.write('{} {} {} {} {} python3 manage.py run_scheduled_task {}\n\n'.format(st.minute, st.hour, st.day_of_month, st.month, st.day_of_week, st.id))
            os.chmod('/etc/periodic/access-server' + str(st.id), 0o777)
            cmd = 'crond -c /etc/periodic/access-server' + str(st.id)
            os.system(cmd)

            return redirect(reverse('manage_task'))
    else:
        form = ScheduleRunForm(instance=task)

    help = """
    This will add a cron job to run this task at a specified time each day.
    """
    
    return render(request, 'add_edit.html', context={'form': form, 'help': help})

def delete_task(request, task_id):
    task = get_object_or_404(ScheduledTask, id=task_id)
    try:
        os.remove('/etc/periodic/access-server' + str(task.id))
    except:
        pass
    task.delete()

    return redirect(reverse('manage_task'))
