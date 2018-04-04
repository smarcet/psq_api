# Generated by Django 2.0.3 on 2018-04-02 14:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_user_bio'),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial', models.CharField(max_length=100)),
                ('friendly_name', models.CharField(max_length=100)),
                ('slots', models.IntegerField()),
            ],
        ),
        migrations.AlterModelOptions(
            name='user',
            options={},
        ),
        migrations.AddField(
            model_name='user',
            name='is_super_admin',
            field=models.BooleanField(default=False, verbose_name='super admin status'),
        ),
        migrations.AddField(
            model_name='device',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owned_devices', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='device',
            name='users',
            field=models.ManyToManyField(related_name='allowed_devices', to=settings.AUTH_USER_MODEL),
        ),
    ]