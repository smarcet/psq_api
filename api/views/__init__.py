from .users import MyUserDetailView, UserList, CreateAdminUserView, CreateRawUserView, UserActivationView, \
    AdminUserDetailView, AdminUserDetailOwnedDevicesView, UserPicUpdateView, AdminUserMyDeviceListView, \
    AdminUsersListView, RawUserDetailView, \
    CreateListUsersView, RetrieveUpdateDestroyUsersView, SuperAdminsDashboardReportView, \
    AdminsDashboardReportView, RegisterGuestUserView, ListUsersSharesView, \
    RawUserDashboardReportView, UserResetPasswordRequestView

from .exercises import ExerciseListCreateAPIView, ExerciseRetrieveUpdateDestroyAPIView, \
    DeviceExercisesDetailView, TutorialListAPIView, ExerciseStatisticsAPIView

from .devices import DeviceOpenRegistrationView, DeviceVerifyView, AdminUserOwnedDevicesManageView, \
    DeviceOpenLocalStreamingStartView, DeviceOpenLocalStreamingEndsView

from .exams import ExamListCreateAPIView, ExamRetrieveUpdateDestroyAPIView, ValidateExamStreamingSignedUrlView

from .device_user_groups import DeviceUsersGroupsListCreateView, DeviceUsersGroupsRetrieveUpdateDestroyAPIView

from .news import NewsListCreateAPIView, NewsRetrieveUpdateDestroyAPIView

from .file_uploads import FileUploadView

from .videos import VideosListAPIView, VideosUsersAPIView, VideoPlayAPIView
