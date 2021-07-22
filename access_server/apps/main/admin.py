from django.contrib import admin

from .models import Action, FirewallDevice


admin.site.register(Action)
admin.site.register(FirewallDevice)
