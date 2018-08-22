# Generated by Django 2.0.3 on 2018-08-22 02:40

import api.managers.user_manager
import api.validators.durations
from django.conf import settings
import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import drf_chunked_upload.models
import macaddress.fields
import model_utils.fields
import storages.backends.gcloud
import uuid


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
                ('date_verified', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('is_verified', models.BooleanField(default=False, verbose_name='verified')),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff status')),
                ('registration_hash', models.CharField(blank=True, max_length=255)),
                ('pic', models.ImageField(blank=True, null=True, upload_to='users')),
                ('role', models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Guest'), (1, 'Student'), (2, 'Teacher'), (3, 'Supervisor')], null=True)),
                ('locale', models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Spanish'), (2, 'English')], default=1, null=True)),
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
                ('serial', models.CharField(default=uuid.uuid4, max_length=255, unique=True)),
                ('mac_address', macaddress.fields.MACAddressField(integer=False, max_length=17, unique=True)),
                ('last_know_ip', models.GenericIPAddressField()),
                ('friendly_name', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('slots', models.PositiveSmallIntegerField(default=3)),
                ('is_active', models.BooleanField(default=False)),
                ('is_verified', models.BooleanField(default=False)),
                ('stream_key', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('slug', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('admins', models.ManyToManyField(blank=True, related_name='managed_devices', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owned_devices', to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(blank=True, related_name='assigned_devices', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DeviceBroadCast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('start_at', models.DateTimeField(null=True)),
                ('ends_at', models.DateTimeField(null=True)),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='broadcasts', to='api.Device')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DeviceUsersGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owned_groups', to=settings.AUTH_USER_MODEL)),
                ('device', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_groups', to='api.Device')),
                ('members', models.ManyToManyField(blank=True, related_name='users_groups', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='update_groups', to=settings.AUTH_USER_MODEL)),
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
                ('duration', models.IntegerField(validators=[api.validators.durations.validate_duration])),
                ('approved', models.BooleanField(default=False)),
                ('evaluated', models.BooleanField(default=False)),
                ('eval_date', models.DateTimeField(null=True)),
                ('video_views', models.IntegerField(default=0)),
                ('device', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exams', to='api.Device')),
                ('evaluator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='evaluated_exams', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExamPendingRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('duration', models.IntegerField(blank=True, null=True)),
                ('is_processed', models.BooleanField(default=False)),
                ('device', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pending_exams_request', to='api.Device')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExamPendingRequestVideo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('file', models.FileField(storage=django.core.files.storage.FileSystemStorage(), upload_to='raw_videos')),
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
                ('title', models.CharField(max_length=255, unique=True)),
                ('abstract', models.TextField()),
                ('max_duration', models.IntegerField(validators=[api.validators.durations.validate_max_duration])),
                ('type', models.PositiveSmallIntegerField(choices=[(1, 'Regular'), (2, 'Tutorial')], default=1, null=True)),
                ('allowed_devices', models.ManyToManyField(blank=True, related_name='allowed_exercises', to='api.Device')),
                ('allowed_tutorials', models.ManyToManyField(blank=True, related_name='related_exercises', to='api.Exercise')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_exercises', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FileUpload',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('file', models.FileField(max_length=255, null=True, storage=django.core.files.storage.FileSystemStorage(), upload_to=drf_chunked_upload.models.generate_filename)),
                ('filename', models.CharField(max_length=255)),
                ('offset', models.BigIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Incomplete'), (2, 'Complete')], default=1)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fileupload', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MailRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('to_address', models.EmailField(max_length=254)),
                ('from_address', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('sent_date', models.DateTimeField(null=True)),
                ('is_sent', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('title', models.CharField(max_length=255, null=True, unique=True)),
                ('body', models.TextField()),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_news', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ResetPasswordRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('request_hash', models.CharField(blank=True, max_length=255)),
                ('processed_date', models.DateTimeField(null=True)),
                ('is_processed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reset_password_request', to=settings.AUTH_USER_MODEL)),
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
                ('type', models.TextField()),
                ('key', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('file', models.FileField(storage=storages.backends.gcloud.GoogleCloudStorage(bucket_name='psq_videos'), upload_to='videos')),
                ('views', models.IntegerField(default=0)),
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
        migrations.AddField(
            model_name='video',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_videos', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='exampendingrequestvideo',
            name='file_upload',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='videos', to='api.FileUpload'),
        ),
        migrations.AddField(
            model_name='exampendingrequestvideo',
            name='request',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='videos', to='api.ExamPendingRequest'),
        ),
        migrations.AddField(
            model_name='exampendingrequest',
            name='exercise',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pending_exams_request', to='api.Exercise'),
        ),
        migrations.AddField(
            model_name='exampendingrequest',
            name='taker',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pending_exams_request', to=settings.AUTH_USER_MODEL),
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
            model_name='exam',
            name='video_shares',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='devicebroadcast',
            name='exercise',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='device_broadcasts', to='api.Exercise'),
        ),
        migrations.AddField(
            model_name='devicebroadcast',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='device_broadcasts', to=settings.AUTH_USER_MODEL),
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
