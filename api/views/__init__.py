from .users import MyUserDetailView, UserList, CreateAdminUserView, CreateRawUserView, UserActivationView,\
    AdminUserDetailView, AdminUserDetailOwnedDevicesView, UserPicUpdateView, AdminUserMyDeviceListView, \
    AdminUsersListView, AdminUserMyExercisesCreateListView
from .exercises import ExerciseListCreateAPIView, ExerciseRetrieveUpdateDestroyAPIView
from .devices import DeviceOpenRegistrationView, DeviceVerifyView, AdminUserOwnedDevicesManageView
from .tutorials import TutorialListCreateAPIView, TutorialRetrieveUpdateDestroyAPIView
from .exams import ExamListCreateAPIView, ExamRetrieveUpdateDestroyAPIView
