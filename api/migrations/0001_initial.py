# Generated by Django 2.0.3 on 2018-04-15 22:58

import api.managers.user_manager
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff status')),
                ('role', models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Student'), (2, 'Teacher'), (3, 'Supervisor')], null=True)),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_users', to=settings.AUTH_USER_MODEL)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_users', to=settings.AUTH_USER_MODEL)),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', api.managers.user_manager.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('serial', models.CharField(max_length=100, unique=True)),
                ('mac_address', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('last_know_ip', models.CharField(blank=True, max_length=50)),
                ('friendly_name', models.CharField(max_length=100, unique=True)),
                ('slots', models.PositiveSmallIntegerField(default=3)),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('admins', models.ManyToManyField(blank=True, related_name='managed_devices', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owned_devices', to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(blank=True, related_name='assigned_devices', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DeviceUsersGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=50)),
                ('device', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_groups', to='api.Device')),
                ('members', models.ManyToManyField(blank=True, related_name='users_groups', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('notes', models.TextField()),
                ('duration', models.DurationField()),
                ('approved', models.BooleanField()),
                ('device', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exams', to='api.Device')),
                ('evaluator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='evaluated_exams', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('title', models.CharField(max_length=100)),
                ('abstract', models.TextField()),
                ('max_duration', models.DurationField()),
                ('type', models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Regular'), (2, 'Tutorial')], null=True)),
                ('allowed_devices', models.ManyToManyField(blank=True, related_name='allowed_exercises', to='api.Device')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_exercises', to=settings.AUTH_USER_MODEL)),
                ('created_from_tutorial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Exercise')),
                ('original_device', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owned_exercises', to='api.Device')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('description', models.TextField()),
                ('url', models.URLField()),
                ('thumbnail', models.URLField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExamVideo',
            fields=[
                ('video_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.Video')),
            ],
            options={
                'abstract': False,
            },
            bases=('api.video',),
        ),
        migrations.CreateModel(
            name='TutorialVideo',
            fields=[
                ('video_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.Video')),
                ('exercise', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='videos', to='api.Exercise')),
            ],
            options={
                'abstract': False,
            },
            bases=('api.video',),
        ),
        migrations.AddField(
            model_name='video',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_videos', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='exam',
            name='exercise',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exams', to='api.Exercise'),
        ),
        migrations.AddField(
            model_name='exam',
            name='taker',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='taked_exams', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='examvideo',
            name='exam',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='videos', to='api.Exam'),
        ),
        migrations.AddField(
            model_name='examvideo',
            name='shares',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
