from django.db import models


class Action(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    name = models.CharField(max_length=30, blank=False, null=False)
    script = models.FileField(blank=False, null=False, upload_to='scripts/')

    def __str__(self):
        return self.name
    
class FirewallDevice(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    name = models.CharField(max_length=30, blank=False, null=False)
    hostname = models.CharField(max_length=30, blank=False, null=False)
    subnet = models.CharField(max_length=30, blank=False, null=False)
    vlan_number = models.IntegerField(blank=False, null=False)
    active = models.BooleanField(default=True)
    notes = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return '{} ({})'.format(self.name, self.hostname)

class ScheduledTask(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    name = models.CharField(max_length=30, blank=False, null=False)
    actions = models.ManyToManyField(Action, related_name='scheduled_tasks_included_in')
    devices = models.ManyToManyField(FirewallDevice, related_name='scheduled_tasks_included_in')
    time_to_run = models.TimeField(null=False, blank=True)

    def __str__(self):
        return self.name
