from .devices import WriteableDeviceSerializer, ReadDeviceSerializer, NullableDeviceSerializer, \
                     OpenRegistrationSerializer, VerifyDeviceSerializer

from .users import WritableUserSerializer, ReadUserSerializer, WritableAdminUserSerializer, \
                   WritableRawUserSerializer, UserPicSerializer, WritableOwnUserSerializer, \
                   ChangePasswordSerializer, RoleWritableUserSerializer

from .exercises import ReadExerciseSerializer, WriteableExerciseSerializer
from .tutorials import TutorialReadSerializer, TutorialWriteSerializer
from .exams import ExamReadSerializer, ExamStudentWriteSerializer, ExamEvaluatorWriteSerializer, \
    ExamVideoWriteSerializer

from .device_users_groups import ReadDeviceUsersGroupSerializer, WriteableDeviceUsersGroupSerializer
