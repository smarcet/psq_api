from .users import MyUserDetailView, UserList, CreateAdminUserView, CreateRawUserView, UserActivationView, \
    AdminUserDetailView, AdminUserDetailOwnedDevicesView, UserPicUpdateView, AdminUserMyDeviceListView, \
    AdminUsersListView, AdminUserMyExercisesListView, RawUserDetailView, \
    CreateListUsersView, RetrieveUpdateDestroyUsersView, SuperAdminsDashboardReportView, \
    AdminsDashboardReportView

from .exercises import ExerciseListCreateAPIView, ExerciseRetrieveUpdateDestroyAPIView, \
    DeviceExercisesDetailView

from .devices import DeviceOpenRegistrationView, DeviceVerifyView, AdminUserOwnedDevicesManageView, \
    DeviceOpenLocalStreamingStartView, DeviceOpenLocalStreamingEndsView

from .tutorials import TutorialListCreateAPIView, TutorialRetrieveUpdateDestroyAPIView

from .exams import ExamListCreateAPIView, ExamRetrieveUpdateDestroyAPIView, ExamUploadAPIView

from .device_user_groups import DeviceUsersGroupsListCreateView

from .news import NewsListCreateAPIView, NewsRetrieveUpdateDestroyAPIView