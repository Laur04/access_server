# Generated by Django 3.2.5 on 2021-07-27 02:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_scheduledtask'),
    ]

    operations = [
        migrations.AddField(
            model_name='firewalldevice',
            name='subnet',
            field=models.CharField(default='100.100.100.0/29', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='firewalldevice',
            name='vlan_number',
            field=models.IntegerField(default=10),
            preserve_default=False,
        ),
    ]
