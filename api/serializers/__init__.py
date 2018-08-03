from .devices import WriteableDeviceSerializer, ReadDeviceSerializer, NullableDeviceSerializer, \
                     OpenRegistrationSerializer, VerifyDeviceSerializer

from .users import WritableUserSerializer, ReadUserSerializer, WritableAdminUserSerializer, \
                   WritableRawUserSerializer, UserPicSerializer, WritableOwnUserSerializer, \
                   ChangePasswordSerializer, RoleWritableUserSerializer, WritableGuestUserSerializer

from .exercises import ReadExerciseSerializer, WriteableExerciseSerializer
from .exams import ExamReadSerializer, ExamStudentWriteSerializer, ExamEvaluatorWriteSerializer, \
    ExamVideoWriteSerializer

from .device_users_groups import ReadDeviceUsersGroupSerializer, WriteableDeviceUsersGroupSerializer

from .news import ReadNewsSerializer, WriteNewsSerializer

from .exam_pending_requests import ExamPendingRequestWriteSerializer, ExamPendingRequestVideoWriteSerializer

from .file_uploads import FileUploadSerializer