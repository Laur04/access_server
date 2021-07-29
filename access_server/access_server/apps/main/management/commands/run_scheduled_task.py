from ansible_playbook_runner import Runner
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from access_server.apps.main.models import ScheduledTask

class Command(BaseCommand):
    help = "Generate traffic from schedued task."

    def add_arguments(self, parser):
        parser.add_argument("task_id", type=str, help="ID of scheduled task to run")

    def handle(self, *args, **kwargs):
        task = ScheduledTask.objects.get(id=int(kwargs['task_id']))

        for h in task.devices.all():
            hostname = h.hostname
            with open(str(settings.MEDIA_ROOT) + '/hosts', 'w') as host_file:
                host_file.write('[{}]\n{}  ansible_ssh_pass={}\n'.format(hostname, hostname, settings.ANSIBLE_SSH_PASS))
            os.environ['ACTION_HOST'] = hostname

            for a in task.actions.all():
                exec("Runner(['{}'], '{}').run()".format(str(settings.MEDIA_ROOT) + '/hosts', a.script.path))
