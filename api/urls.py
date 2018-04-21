from rest_framework_jwt.views import (obtain_jwt_token)
from django.urls import path
from .views.users import UserDetailMe, UserList, CreateRawUserView, CreateAdminUserView, UserValidateView, AdminUserPicView
from .views.devices import DeviceListCreate, DeviceDetail, DeviceUsersList, DeviceAdminsList
from .views import ExerciseListCreateAPIView, ExerciseRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('token', obtain_jwt_token, name='get-token'),
    path('users/me', UserDetailMe.as_view(), name='get-my-user'),
    path('users/validate/<slug:registration_token>', UserValidateView.as_view(), name='validate-user'),
    path('admin-users', CreateAdminUserView.as_view(), name='create-list-admin-users'),
    path('admin-users/<int:pk>/pic', AdminUserPicView.as_view(), name='admin-user-pic'),
    path('raw-users', CreateRawUserView.as_view(), name='create-list-raw-users'),
    path('devices', DeviceListCreate.as_view(), name='device-list-create'),
    path('devices/<int:pk>', DeviceDetail.as_view(), name='device-detail'),
    path('devices/<int:pk>/users/<int:user_id>', DeviceUsersList.as_view(), name='device-users'),
    path('devices/<int:pk>/admins/<int:user_id>', DeviceAdminsList.as_view(), name='device-admins'),
    path('exercises', ExerciseListCreateAPIView.as_view(), name='exercises-list-create'),
    path('exercises/<int:pk>', ExerciseRetrieveUpdateDestroyAPIView.as_view(), name='exercises-retrieve-update-destroy'),
]