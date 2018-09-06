from django.urls import path
from rest_framework_jwt.views import (obtain_jwt_token, refresh_jwt_token)

from .views import FileUploadView, VideosListAPIView, VideosUsersAPIView, VideoPlayAPIView
from .views import ExerciseListCreateAPIView, ExerciseRetrieveUpdateDestroyAPIView, DeviceOpenRegistrationView, \
    ExamListCreateAPIView, \
    ExamRetrieveUpdateDestroyAPIView, DeviceOpenLocalStreamingStartView, DeviceOpenLocalStreamingEndsView, \
    DeviceUsersGroupsListCreateView, NewsListCreateAPIView, NewsRetrieveUpdateDestroyAPIView, \
    ValidateExamStreamingSignedUrlView, DeviceUsersGroupsRetrieveUpdateDestroyAPIView
from .views.devices import DeviceListCreateView, DeviceDetailView, DeviceUsersListView, DeviceAdminsListView, \
    DeviceVerifyView, \
    AdminUserOwnedDevicesManageView
from .views.exercises import DeviceExercisesDetailView, TutorialListAPIView, ShareExerciseAPIView, ExerciseStatisticsAPIView
from .views.users import MyUserDetailView, CreateRawUserView, CreateAdminUserView, UserActivationView, \
    UserPicUpdateView, AdminUserDetailView, AdminUserDetailOwnedDevicesView, AdminUserMyDeviceListView, \
    UserResendVerificationView, NonSuperAdminUsersListView, AdminUsersListView, \
    ListMyUsersUserView, RawUserDetailView, \
    CreateListUsersView, RetrieveUpdateDestroyUsersView, SuperAdminsDashboardReportView, AdminsDashboardReportView, \
    RegisterGuestUserView, ListUsersSharesView, RawUserDashboardReportView, UserResetPasswordRequestView

urlpatterns = [
    # https://getblimp.github.io/django-rest-framework-jwt/
    path('token/refresh', refresh_jwt_token, name='refresh-token'),
    path('token', obtain_jwt_token, name='get-token'),
    # users
    path('users/me/exclude', ListUsersSharesView.as_view(), name='list-users-shares'),
    path('users', CreateListUsersView.as_view(), name='create-list-users'),
    path('users/<int:pk>', RetrieveUpdateDestroyUsersView.as_view(), name='user-details'),
    path('users/me/pic', UserPicUpdateView.as_view(), name='user-pic'),
    path('users/me', MyUserDetailView.as_view(), name='my-user-details'),
    path('users/non-super-admin', NonSuperAdminUsersListView.as_view(), name='non-super-admin-users-list'),
    path('users/admins', AdminUsersListView.as_view(), name='admin-users-list'),
    path('users/created-by/me', ListMyUsersUserView.as_view(), name='users-created-by-me'),
    path('users/<int:pk>/verification/resend', UserResendVerificationView.as_view(), name='user-verification-resend'),
    path('users/activate/<slug:registration_token>', UserActivationView.as_view(), name='activate-user'),
    path('users/reset-password-requests/<slug:registration_token>',  UserResetPasswordRequestView.as_view(), name='do-reset-password-user'),
    path('users/reset-password-requests',  UserResetPasswordRequestView.as_view(), name='reset-password-request-user'),
    # device user groups
    path('users/me/devices/all/user-groups', DeviceUsersGroupsListCreateView.as_view(), name="device-user-groups-list"),
    path('users/me/devices/all/user-groups/<int:pk>', DeviceUsersGroupsRetrieveUpdateDestroyAPIView.as_view(), name="device-user-groups-details"),
    # super admins
    path('super-admins/dashboard-report', SuperAdminsDashboardReportView.as_view(), name='super-admin-dashboard-report'),
    # admin users
    path('admin-users', CreateAdminUserView.as_view(), name='create-list-admin-users'),
    path('admin-users/me/devices', AdminUserMyDeviceListView.as_view(), name='admin-user-my-devices'),
    path('admin-users/<int:pk>/owned-devices/<int:device_id>', AdminUserOwnedDevicesManageView.as_view(),
         name='admin-user-owned-devices-manage'),
    path('admin-users/<int:pk>/owned-devices', AdminUserDetailOwnedDevicesView.as_view(), name='admin-user-devices'),
    path('admin-users/<int:pk>', AdminUserDetailView.as_view(), name='admin-users'),
    path('admin-users/dashboard-report', AdminsDashboardReportView.as_view(), name='admin-dashboard-report'),
    # raw users
    path('raw-users', CreateRawUserView.as_view(), name='create-list-raw-users'),
    path('raw-users/<int:pk>', RawUserDetailView.as_view(), name='raw-users'),
    path('raw-users/dashboard-report', RawUserDashboardReportView.as_view(), name='raw-user-dashboard-report'),
    # guest users
    path('guest-users', RegisterGuestUserView.as_view(), name='register-guest-users'),
    # Devices
    path('devices', DeviceListCreateView.as_view(), name='device-list-create'),
    path('devices/current/registration', DeviceOpenRegistrationView.as_view(), name='device-open-registration'),
    path('devices/streaming/publish/start', DeviceOpenLocalStreamingStartView.as_view(), name='device-local-streaming-publish-start'),
    path('devices/streaming/publish/finish', DeviceOpenLocalStreamingEndsView.as_view(), name='device-open-streaming-publish-done'),
    path('devices/<int:pk>/verify', DeviceVerifyView.as_view(), name='device-verify'),
    path('devices/<int:pk>', DeviceDetailView.as_view(), name='device-detail'),
    path('devices/<int:pk>/exercises', DeviceExercisesDetailView.as_view(), name='device-exercises'),
    path('devices/<int:pk>/users/<int:user_id>', DeviceUsersListView.as_view(), name='device-users'),
    path('devices/<int:pk>/admins/<int:user_id>', DeviceAdminsListView.as_view(), name='device-admins'),
    # exercises
    path('exercises', ExerciseListCreateAPIView.as_view(), name='exercises-list-create'),
    path('tutorials', TutorialListAPIView.as_view(), name='tutorials-list-create'),
    path('exercises/<int:pk>', ExerciseRetrieveUpdateDestroyAPIView.as_view(), name='exercises-retrieve-update-destroy'),
    path('exercises/<int:pk>/statistics/<int:start_date>/<int:end_date>', ExerciseStatisticsAPIView.as_view(), name='exercises-statistics'),
    path('exercises/<int:pk>/devices/<int:device_id>', ShareExerciseAPIView.as_view(), name='share-exercises'),
    # exams
    path('exams/upload', FileUploadView.as_view(), name='exams-upload'),
    path('exams/upload/<uuid:pk>', FileUploadView.as_view(), name='exams-upload-details'),
    path('exams', ExamListCreateAPIView.as_view(), name='exams-list-create'),
    path('exams/<int:pk>', ExamRetrieveUpdateDestroyAPIView.as_view(), name='exams-retrieve-update-destroy'),
    path('streaming/validate', ValidateExamStreamingSignedUrlView.as_view(), name='validate-streaming'),
    # videos
    path('videos', VideosListAPIView.as_view(), name='videos-list'),
    path('videos/<int:pk>/play', VideoPlayAPIView.as_view(), name='videos-play'),
    path('videos/<int:pk>/users/<int:user_id>/share', VideosUsersAPIView.as_view(), name='videos-users'),
    # news
    path('news', NewsListCreateAPIView.as_view(), name="news-list-create"),
    path('news/<int:pk>', NewsRetrieveUpdateDestroyAPIView.as_view(), name="news-retrieve-update-destroy")
]
