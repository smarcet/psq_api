# Generated by Django 2.0.3 on 2018-04-02 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20180402_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='slots',
            field=models.PositiveSmallIntegerField(default=3),
        ),
    ]
