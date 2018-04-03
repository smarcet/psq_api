from rest_framework_jwt.views import (obtain_jwt_token)
from django.urls import path
from .views import *

urlpatterns = [
    path('token', obtain_jwt_token),
    path('users/me', UserDetailMe.as_view()),
    path('users', UserList.as_view()),
]