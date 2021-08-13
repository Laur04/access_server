from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('status', views.status, name='status'),
    path('run/<str:device_id>/<str:action_id>', views.run_action, name='run_action'),
    path('manage/action', views.manage_action, name='manage_action'),
    path('manage/device', views.manage_device, name='manage_device'),
    path('manage/task', views.manage_task, name='manage_task'),
    path('add/action', views.add_action, name='add_action'),
    path('add/device', views.add_device, name='add_device'),
    path('add/task', views.add_task, name='add_task'),
    path('edit/action/<int:action_id>', views.edit_action, name='edit_action'),
    path('edit/device/<int:device_id>', views.edit_device, name='edit_device'),
    path('edit/task/<int:task_id>', views.edit_task, name='edit_task'),
    path('delete/action/<int:action_id>', views.delete_action, name='delete_action'),
    path('delete/device/<int:device_id>', views.delete_device, name='delete_device'),
    path('delete/task/<int:task_id>', views.delete_task, name='delete_task'),
]
