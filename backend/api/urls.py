from rest_framework_jwt.views import (obtain_jwt_token)
from django.urls import path
from .views.users import UserDetailMe, UserList
from .views.devices import DeviceList

urlpatterns = [
    path('token', obtain_jwt_token),
    path('users/me', UserDetailMe.as_view()),
    path('users', UserList.as_view()),
    path('devices', DeviceList.as_view()),
]