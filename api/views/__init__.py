from .users import MyUserDetailView, UserList, CreateAdminUserView, CreateRawUserView, UserActivationView, \
    AdminUserDetailView, AdminUserDetailOwnedDevicesView, UserPicUpdateView, AdminUserMyDeviceListView, \
    AdminUsersListView, AdminUserMyExercisesListView, RawUserDetailView, \
    CreateListUsersView, RetrieveUpdateDestroyUsersView, SuperAdminsDashboardReportView, \
    AdminsDashboardReportView, RegisterGuestUserView, ListUsersSharesView

from .exercises import ExerciseListCreateAPIView, ExerciseRetrieveUpdateDestroyAPIView, \
    DeviceExercisesDetailView, TutorialListAPIView

from .devices import DeviceOpenRegistrationView, DeviceVerifyView, AdminUserOwnedDevicesManageView, \
    DeviceOpenLocalStreamingStartView, DeviceOpenLocalStreamingEndsView

from .exams import ExamListCreateAPIView, ExamRetrieveUpdateDestroyAPIView, ValidateExamStreamingSignedUrlView

from .device_user_groups import DeviceUsersGroupsListCreateView

from .news import NewsListCreateAPIView, NewsRetrieveUpdateDestroyAPIView

from .file_uploads import FileUploadView

from .videos import VideosListAPIView, VideosUsersAPIView, VideoPlayAPIView
