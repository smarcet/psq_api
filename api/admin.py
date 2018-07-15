from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ugettext_lazy as _
from .models import Device
from .models import DeviceUsersGroup
from .models import Exam
from .models import ExamVideo
from .models import Exercise
from .models import MailRequest
from .models import Tutorial
from .models import TutorialVideo
from .models import User
from .models import DeviceBroadCast


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = '__all__'

    def clean(self):
        users = self.cleaned_data.get('users')
        slots = self.cleaned_data.get('slots')
        if users and users.count() > slots:
            raise ValidationError(_('Maximum {slots} users are allowed.').format(slots=slots))

        return self.cleaned_data


class DeviceAdmin(admin.ModelAdmin):
    form = DeviceForm


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = '__all__'


class ExamAdmin(admin.ModelAdmin):
    form = ExamForm


class MyUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'role', 'created_by', 'updated_by','is_verified', 'date_verified', 'pic')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)
    filter_horizontal = ()

    # Static overriding
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'bio', 'pic')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'is_verified' )}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


admin.site.register(User, MyUserAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(Tutorial)
admin.site.register(Exercise)
admin.site.register(ExamVideo)
admin.site.register(TutorialVideo)
admin.site.register(DeviceUsersGroup)
admin.site.unregister(Group)
admin.site.register(MailRequest)
admin.site.register(DeviceBroadCast)

admin.site.site_header = 'PSQ Admin'
