from rest_framework_jwt.views import (obtain_jwt_token, refresh_jwt_token)
from django.urls import path
from .views.users import UserDetailMe, CreateRawUserView, CreateAdminUserView, UserValidateView, \
    UserPicView, AdminUserDetail, AdminUserDetailOwnedDevices
from .views.devices import DeviceListCreate, DeviceDetail, DeviceUsersList, DeviceAdminsList, DeviceVerifyView, \
    AdminUserOwnedDevicesManageView
from .views import ExerciseListCreateAPIView, ExerciseRetrieveUpdateDestroyAPIView, DeviceOpenRegistrationView, \
    TutorialRetrieveUpdateDestroyAPIView, TutorialListCreateAPIView, ExamListCreateAPIView, \
    ExamRetrieveUpdateDestroyAPIView

urlpatterns = [
    # https://getblimp.github.io/django-rest-framework-jwt/
    path('token/refresh', refresh_jwt_token, name='refresh-token'),
    path('token', obtain_jwt_token, name='get-token'),
    path('users/me/pic', UserPicView.as_view(), name='user-pic'),
    path('users/me', UserDetailMe.as_view(), name='my-user-details'),
    path('users/validate/<slug:registration_token>', UserValidateView.as_view(), name='validate-user'),
    path('admin-users', CreateAdminUserView.as_view(), name='create-list-admin-users'),
    path('admin-users/<int:pk>/owned-devices/<int:device_id>', AdminUserOwnedDevicesManageView.as_view(),
         name='admin-user-owned-devices-manage'),
    path('admin-users/<int:pk>/owned-devices', AdminUserDetailOwnedDevices.as_view(), name='admin-user-devices'),

    path('admin-users/<int:pk>', AdminUserDetail.as_view(), name='admin-user'),
    path('raw-users', CreateRawUserView.as_view(), name='create-list-raw-users'),
    path('devices', DeviceListCreate.as_view(), name='device-list-create'),
    path('devices/registration', DeviceOpenRegistrationView.as_view(), name='device-open-registration'),
    path('devices/<int:pk>/verify', DeviceVerifyView.as_view(), name='device-verify'),
    path('devices/<int:pk>', DeviceDetail.as_view(), name='device-detail'),
    path('devices/<int:pk>/users/<int:user_id>', DeviceUsersList.as_view(), name='device-users'),
    path('devices/<int:pk>/admins/<int:user_id>', DeviceAdminsList.as_view(), name='device-admins'),
    path('exercises', ExerciseListCreateAPIView.as_view(), name='exercises-list-create'),
    path('exercises/<int:pk>', ExerciseRetrieveUpdateDestroyAPIView.as_view(),
         name='exercises-retrieve-update-destroy'),
    path('tutorials', TutorialListCreateAPIView.as_view(), name='tutorials-list-create'),
    path('tutorials/<int:pk>', TutorialRetrieveUpdateDestroyAPIView.as_view(),
         name='tutorials-retrieve-update-destroy'),
    path('exams', ExamListCreateAPIView.as_view(), name='exams-list-create'),
    path('exams/<int:pk>', ExamRetrieveUpdateDestroyAPIView.as_view(), name='exams-retrieve-update-destroy'),
]
