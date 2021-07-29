from django.contrib import admin

from .models import Action, FirewallDevice, ScheduledTask


admin.site.register(Action)
admin.site.register(FirewallDevice)
admin.site.register(ScheduledTask)
