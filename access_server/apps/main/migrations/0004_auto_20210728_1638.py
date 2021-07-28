# Generated by Django 3.2.5 on 2021-07-28 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20210727_0251'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scheduledtask',
            name='time_to_run',
        ),
        migrations.AddField(
            model_name='scheduledtask',
            name='day_of_month',
            field=models.CharField(default='*', max_length=20),
        ),
        migrations.AddField(
            model_name='scheduledtask',
            name='day_of_week',
            field=models.CharField(default='*', help_text='Sunday is 0', max_length=20),
        ),
        migrations.AddField(
            model_name='scheduledtask',
            name='hour',
            field=models.CharField(default='*', max_length=20),
        ),
        migrations.AddField(
            model_name='scheduledtask',
            name='minute',
            field=models.CharField(default='*', max_length=20),
        ),
        migrations.AddField(
            model_name='scheduledtask',
            name='month',
            field=models.CharField(default='*', help_text='January is 1', max_length=20),
        ),
    ]