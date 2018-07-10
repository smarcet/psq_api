from .users import MyUserDetailView, UserList, CreateAdminUserView, CreateRawUserView, UserActivationView,\
    AdminUserDetailView, AdminUserDetailOwnedDevicesView, UserPicUpdateView, AdminUserMyDeviceListView, \
    AdminUsersListView, AdminUserMyExercisesListView, RawUserDetailView, UserDetailsView
from .exercises import ExerciseListCreateAPIView, ExerciseRetrieveUpdateDestroyAPIView, DeviceExercisesDetailView
from .devices import DeviceOpenRegistrationView, DeviceVerifyView, AdminUserOwnedDevicesManageView
from .tutorials import TutorialListCreateAPIView, TutorialRetrieveUpdateDestroyAPIView
from .exams import ExamListCreateAPIView, ExamRetrieveUpdateDestroyAPIView, ExamUploadAPIView
