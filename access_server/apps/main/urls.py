from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('add/action', views.add_action, name='add_action'),
    path('add/device', views.add_device, name='add_device'),
]
