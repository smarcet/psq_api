from rest_framework_jwt.views import (obtain_jwt_token)
from django.urls import path
from .views.users import UserDetailMe, UserList
from .views.devices import DeviceList, DeviceDetail, DeviceUsersList, DeviceAdminsList

urlpatterns = [
    path('token', obtain_jwt_token),
    path('users/me', UserDetailMe.as_view()),
    path('users', UserList.as_view()),
    path('admin-users', UserList.as_view()),
    path('raw-users', UserList.as_view()),
    path('devices', DeviceList.as_view()),
    path('devices/<int:pk>', DeviceDetail.as_view()),
    path('devices/<int:pk>/users/<int:user_id>', DeviceUsersList.as_view()),
    path('devices/<int:pk>/admins/<int:user_id>', DeviceAdminsList.as_view()),
]