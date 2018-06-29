from rest_framework_jwt.views import (obtain_jwt_token, refresh_jwt_token)
from django.urls import path
from .views.users import MyUserDetailView, CreateRawUserView, CreateAdminUserView, UserActivationView, \
    UserPicUpdateView, AdminUserDetailView, AdminUserDetailOwnedDevicesView, AdminUserMyDeviceListView, \
    UserResendVerificationView, NonSuperAdminUsersListView, AdminUsersListView
from .views.devices import DeviceListCreateView, DeviceDetailView, DeviceUsersListView, DeviceAdminsListView, DeviceVerifyView, \
    AdminUserOwnedDevicesManageView
from .views import ExerciseListCreateAPIView, ExerciseRetrieveUpdateDestroyAPIView, DeviceOpenRegistrationView, \
    TutorialRetrieveUpdateDestroyAPIView, TutorialListCreateAPIView, ExamListCreateAPIView, \
    ExamRetrieveUpdateDestroyAPIView

urlpatterns = [
    # https://getblimp.github.io/django-rest-framework-jwt/
    path('token/refresh', refresh_jwt_token, name='refresh-token'),
    path('token', obtain_jwt_token, name='get-token'),
    path('users/me/pic', UserPicUpdateView.as_view(), name='user-pic'),
    path('users/me', MyUserDetailView.as_view(), name='my-user-details'),
    path('users/non-super-admin', NonSuperAdminUsersListView.as_view(), name='non-super-admin-users-list'),
    path('users/admins', AdminUsersListView.as_view(), name='admin-users-list'),
    path('users/<int:pk>/verification/resend', UserResendVerificationView.as_view(), name='user-verification-resend'),
    path('users/activate/<slug:registration_token>', UserActivationView.as_view(), name='activate-user'),
    path('admin-users', CreateAdminUserView.as_view(), name='create-list-admin-users'),
    path('admin-users/me/devices', AdminUserMyDeviceListView.as_view(), name='admin-user-my-devices'),
    path('admin-users/<int:pk>/owned-devices/<int:device_id>', AdminUserOwnedDevicesManageView.as_view(),
         name='admin-user-owned-devices-manage'),
    path('admin-users/<int:pk>/owned-devices', AdminUserDetailOwnedDevicesView.as_view(), name='admin-user-devices'),
    path('admin-users/<int:pk>', AdminUserDetailView.as_view(), name='admin-user'),
    path('raw-users', CreateRawUserView.as_view(), name='create-list-raw-users'),
    path('devices', DeviceListCreateView.as_view(), name='device-list-create'),
    path('devices/registration', DeviceOpenRegistrationView.as_view(), name='device-open-registration'),
    path('devices/<int:pk>/verify', DeviceVerifyView.as_view(), name='device-verify'),
    path('devices/<int:pk>', DeviceDetailView.as_view(), name='device-detail'),
    path('devices/<int:pk>/users/<int:user_id>', DeviceUsersListView.as_view(), name='device-users'),
    path('devices/<int:pk>/admins/<int:user_id>', DeviceAdminsListView.as_view(), name='device-admins'),
    path('exercises', ExerciseListCreateAPIView.as_view(), name='exercises-list-create'),
    path('exercises/<int:pk>', ExerciseRetrieveUpdateDestroyAPIView.as_view(),
         name='exercises-retrieve-update-destroy'),
    path('tutorials', TutorialListCreateAPIView.as_view(), name='tutorials-list-create'),
    path('tutorials/<int:pk>', TutorialRetrieveUpdateDestroyAPIView.as_view(),
         name='tutorials-retrieve-update-destroy'),
    path('exams', ExamListCreateAPIView.as_view(), name='exams-list-create'),
    path('exams/<int:pk>', ExamRetrieveUpdateDestroyAPIView.as_view(), name='exams-retrieve-update-destroy'),
]
