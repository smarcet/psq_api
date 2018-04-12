# Generated by Django 2.0.3 on 2018-04-12 02:21

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='admins',
            field=models.ManyToManyField(blank=True, related_name='managed_devices', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='device',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='assigned_devices', to=settings.AUTH_USER_MODEL),
        ),
    ]
