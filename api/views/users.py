import hashlib
from django.db.models import Q, Count
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, \
    ListAPIView, RetrieveUpdateAPIView, CreateAPIView

from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.exceptions import CustomValidationError
from ..decorators import role_required
from ..models import ModelValidationException, Exercise
from ..models import User, Device, Exam, DeviceUsersGroup, News
from ..serializers import ReadExerciseSerializer
from ..serializers.devices import ReadDeviceSerializer
from ..serializers.users import ReadUserSerializer, WritableAdminUserSerializer, \
    WritableRawUserSerializer, UserPicSerializer, WritableOwnUserSerializer, \
    ChangePasswordSerializer, RoleWritableUserSerializer, WritableGuestUserSerializer
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz


class UserResendVerificationView(APIView):

    @role_required(required_role=User.TEACHER)
    def post(self, request, pk):
        user = User.objects.get(pk=pk)
        if user is None:
            return Response(status=404, data=_("User not found"))
        user.resend_verification()
        return Response(status=204)


class UserActivationView(APIView):
    parser_classes = (JSONParser,)

    # this view is open to anyone with a valid token, if u have the token
    # its bc u mean to have it !
    permission_classes = (AllowAny,)

    def post(self, request, registration_token):
        json = request.data
        password = json.get("password", None)

        if registration_token is None:
            return Response(status=400, data=_("Missing param 'registration_token'"))

        if password is None:
            return Response(status=400, data=_("Missing param 'password'"))

        user = User.objects.filter(
            registration_hash=hashlib.md5(registration_token.encode('utf-8')).hexdigest()).first()

        if user is None:
            return Response(status=404, data=_("User not found"))

        if user.is_verified:
            return Response(status=404, data=_("User not found"))

        user.verify(password)

        return Response(status=201)


class UserList(APIView):

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = ReadUserSerializer(users, many=True)
        return Response(serializer.data)


class UserPicUpdateView(APIView):
    serializer_class = UserPicSerializer
    parser_classes = (MultiPartParser, FormParser)

    @staticmethod
    def post(request):
        pic_serializer = UserPicSerializer(instance=request.user, data=request.data, partial=True)
        if pic_serializer.is_valid():
            pic_serializer.save()
            response_data = pic_serializer.data
            response_data['pic_url'] = request.build_absolute_uri(response_data['pic'])
            return Response(data=response_data, status=status.HTTP_201_CREATED)

        return Response(pic_serializer.errors, status=status.HTTP_412_PRECONDITION_FAILED)


class AdminUserMyDeviceListView(ListAPIView):
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('friendly_name', 'ip', 'serial')
    ordering_fields = ('id', 'friendly_name')

    def get_serializer_class(self):
        return ReadDeviceSerializer

    @role_required(required_role=User.TEACHER)
    def get(self, request, *args, **kwargs):
        admin_user = request.user
        queryset = self.filter_queryset(
            Device.objects.filter(Q(owner=admin_user) | Q(admins__in=[admin_user])).distinct())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AdminUserMyExercisesListView(ListAPIView):
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('title', 'abstract',)
    ordering_fields = ('id', 'title')

    def get_serializer_class(self):
        return ReadExerciseSerializer

    @role_required(required_role=User.TEACHER)
    def get(self, request, *args, **kwargs):
        admin_user = request.user
        queryset = self.filter_queryset(Exercise.objects.filter(
            Q(allowed_devices__owner=admin_user) | Q(author=admin_user) | Q(
                allowed_devices__admins__in=[admin_user])).distinct())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AdminUserDetailOwnedDevicesView(ListAPIView):

    def get_serializer_class(self):
        return ReadDeviceSerializer

    @role_required(required_role=User.SUPERVISOR)
    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        admin_user = User.objects.get(pk=pk)
        queryset = self.filter_queryset(Device.objects.filter(owner=admin_user))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RawUserDetailView(RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        if self.request.method == 'PUT':
            return User.objects
        return User.objects.filter(role=User.STUDENT)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WritableRawUserSerializer
        if self.request.method == 'PUT':
            return RoleWritableUserSerializer
        return ReadUserSerializer

    def patch(self, request, *args, **kwargs):
        pass

    @role_required(required_role=User.TEACHER)
    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            current_user = self.request.user

            if current_user.role == User.TEACHER and instance.created_by.id != current_user.id:
                raise ModelValidationException(_('user was not created by current user'))

            return self.destroy(request, *args, **kwargs)
        except ModelValidationException as error1:
            raise CustomValidationError(str(error1), 'error')

    @role_required(required_role=User.TEACHER)
    def put(self, request, *args, **kwargs):
        try:
            return self.partial_update(request, *args, **kwargs)

        except ModelValidationException as error1:
            raise CustomValidationError(str(error1), 'error')


class AdminUserDetailView(RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        if self.request.method == 'PUT':
            return User.objects
        return User.objects.filter(role=User.TEACHER)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WritableAdminUserSerializer
        if self.request.method == 'PUT':
            return RoleWritableUserSerializer
        return ReadUserSerializer

    def patch(self, request, *args, **kwargs):
        pass

    @role_required(required_role=User.TEACHER)
    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            current_user = self.request.user

            if current_user.role == User.TEACHER and instance.created_by.id != current_user.id:
                raise ModelValidationException(_('user was not created by current user'))

            return self.destroy(request, *args, **kwargs)
        except ModelValidationException as error1:
            raise CustomValidationError(str(error1), 'error')

    @role_required(required_role=User.TEACHER)
    def put(self, request, *args, **kwargs):
        try:
            return self.partial_update(request, *args, **kwargs)

        except ModelValidationException as error1:
            raise CustomValidationError(str(error1), 'error')


class NonSuperAdminUsersListView(ListAPIView):
    serializer_class = ReadUserSerializer
    queryset = User.objects.filter((Q(role=User.TEACHER) | Q(role=User.STUDENT)))
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('email', 'first_name', 'last_name')
    ordering_fields = ('id', 'email', 'first_name', 'last_name')

    @role_required(required_role=User.TEACHER)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class AdminUsersListView(ListAPIView):
    serializer_class = ReadUserSerializer
    queryset = User.objects.filter((Q(role=User.TEACHER)))
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('email', 'first_name', 'last_name')
    ordering_fields = ('id', 'email', 'first_name', 'last_name')

    @role_required(required_role=User.TEACHER)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ListMyUsersUserView(ListCreateAPIView):
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('email', 'first_name', 'last_name')
    ordering_fields = ('id', 'email', 'first_name', 'last_name')

    def get_queryset(self):
        return User.objects.filter(created_by=self.request.user)

    def get_serializer_class(self):
        return ReadUserSerializer

    @role_required(required_role=User.TEACHER)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CreateAdminUserView(ListCreateAPIView):
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('email', 'first_name', 'last_name')
    ordering_fields = ('id', 'email', 'first_name', 'last_name')
    queryset = User.objects.filter(role=User.TEACHER)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WritableAdminUserSerializer
        return ReadUserSerializer

    @role_required(required_role=User.SUPERVISOR)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @role_required(required_role=User.TEACHER)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CreateRawUserView(ListCreateAPIView):
    queryset = User.objects.filter(role=User.STUDENT)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WritableRawUserSerializer
        return ReadUserSerializer

    @role_required(required_role=User.TEACHER)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class MyUserDetailView(RetrieveUpdateAPIView):

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return WritableOwnUserSerializer
        return ReadUserSerializer

    def get_object(self):
        return self.request.user

    def get(self, request, **kwargs):
        user = self.get_object()
        serializer = ReadUserSerializer(user, context={"request": request})
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        try:
            data = request.data
            if 'password' in data and data['password'] is not None:
                instance = self.get_object()
                serializer = ChangePasswordSerializer(data=request.data)
                if serializer.is_valid(True):
                    # set_password also hashes the password that the user will get
                    instance.set_password(serializer.data.get("password"))
                    instance.save()

            return self.partial_update(request, *args, **kwargs)
        except ModelValidationException as error1:
            raise CustomValidationError(str(error1), 'error')


class RetrieveUpdateDestroyUsersView(RetrieveUpdateDestroyAPIView):

    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return RoleWritableUserSerializer
        return ReadUserSerializer

    @role_required(required_role=User.TEACHER)
    def get(self, request, *args, **kwargs):
        try:
            current_user = request.user
            user = self.get_object()
            if current_user.role == User.TEACHER and user.created_by.id != current_user.id:
                raise ModelValidationException(_('user was not created by current user'))
            return self.retrieve(request, *args, **kwargs)
        except ModelValidationException as error1:
            raise CustomValidationError(str(error1), 'error')

    @role_required(required_role=User.TEACHER)
    def put(self, request, *args, **kwargs):
        current_user = request.user
        instance = self.get_object()
        if not current_user.can_update_user(instance):
            raise CustomValidationError(_('user can not update this user'), 'error')
        return self.partial_update(request, *args, **kwargs)

    @role_required(required_role=User.TEACHER)
    def patch(self, request, *args, **kwargs):
        pass

    @role_required(required_role=User.TEACHER)
    def delete(self, request, *args, **kwargs):
        current_user = request.user
        instance = self.get_object()
        if not current_user.can_delete_user(instance):
            raise CustomValidationError(_('user can not delete this user'), 'error')

        return self.destroy(request, *args, **kwargs)


class CreateListUsersView(ListCreateAPIView):
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('first_name', 'last_name', 'email')
    ordering_fields = ('id', 'first_name', 'last_name', 'email')

    def get_queryset(self):
        return User.objects.filter(~Q(id=self.request.user.id)).order_by('id')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RoleWritableUserSerializer
        return ReadUserSerializer

    @role_required(required_role=User.TEACHER)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @role_required(required_role=User.TEACHER)
    def post(self, request, *args, **kwargs):
        role = request.data['role']
        current_user = request.user
        if not current_user.can_create_role(role):
            raise CustomValidationError("user {user_id} can not create users with role {role}".format(
                user_id=current_user.id,
                role=role
            ), 'error')
        return self.create(request, *args, **kwargs)


class SuperAdminsDashboardReportView(APIView):

    @role_required(required_role=User.SUPERVISOR)
    def get(self, request, months_qty=6):

        now = datetime.utcnow().replace(hour=00, minute=00, day=1, second=0, microsecond=0)
        end_now = now + relativedelta(months=+1, days=-1)
        dates = [
            (
                now.replace(hour=00, minute=00, day=1, second=0, microsecond=0, tzinfo=pytz.UTC),
                end_now.replace(hour=23, minute=59, second=59, tzinfo=pytz.UTC, microsecond=999999)
            )
        ]

        for x in range(1, months_qty):
            start = now + relativedelta(months=-x)
            end = start + relativedelta(months=+1, days=-1)
            dates.append((
                start.replace(hour=00, minute=00, day=1, second=0, microsecond=0, tzinfo=pytz.UTC),
                end.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=pytz.UTC)
            ))

        users_per_month = []
        devices_per_month = []

        for dates_tuple in reversed(dates):
            users_per_month.append(
                User.objects.filter(Q(date_joined__gte=dates_tuple[0]) & Q(date_joined__lte=dates_tuple[1])).count())
            devices_per_month.append(
                Device.objects.filter(Q(created__gte=dates_tuple[0]) & Q(created__lte=dates_tuple[1])).count())

        data = {
            'users_per_month': users_per_month,
            'devices_per_month': devices_per_month,
            'super_admin_user_qty': User.objects.filter(role=User.SUPERVISOR).count(),
            'admin_user_qty': User.objects.filter(role=User.TEACHER).count(),
            'raw_user_qty': User.objects.filter(role=User.STUDENT).count(),
            'devices_qty': Device.objects.count(),
        }

        return Response(data, status=200)


class AdminsDashboardReportView(APIView):

    @role_required(required_role=User.TEACHER)
    def get(self, request, months_qty=6):

        now = datetime.utcnow().replace(hour=00, minute=00, day=1, second=0, microsecond=0)
        end_now = now + relativedelta(months=+1, days=-1)
        dates = [
            (
                now.replace(hour=00, minute=00, day=1, second=0, microsecond=0, tzinfo=pytz.UTC),
                end_now.replace(hour=23, minute=59, second=59, tzinfo=pytz.UTC, microsecond=999999)
            )
        ]

        for x in range(1, months_qty):
            start = now + relativedelta(months=-x)
            end = start + relativedelta(months=+1, days=-1)
            dates.append((
                start.replace(hour=00, minute=00, day=1, second=0, microsecond=0, tzinfo=pytz.UTC),
                end.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=pytz.UTC)
            ))

        exams_evaluated_per_month = []
        exams_approved_per_month = []
        exams_reject_per_month = []
        exams_evaluated_qty = 0
        exams_approved_qty = 0
        exams_reject_qty = 0

        for dates_tuple in reversed(dates):
            q1 =  Exam.objects.filter(Q(eval_date__gte=dates_tuple[0]) & Q(eval_date__lte=dates_tuple[1]) & Q(
                    evaluator=request.user) & Q(exercise__type=Exercise.REGULAR)).count()
            exams_evaluated_qty += q1
            exams_evaluated_per_month.append(q1)
            q2 = Exam.objects.filter(
                Q(eval_date__gte=dates_tuple[0]) & Q(eval_date__lte=dates_tuple[1]) & Q(evaluator=request.user) & Q(
                    approved=True) & Q(exercise__type=Exercise.REGULAR)).count()
            exams_approved_per_month.append(q2)
            exams_approved_qty += q2
            q3 = Exam.objects.filter(
                    Q(eval_date__gte=dates_tuple[0]) & Q(eval_date__lte=dates_tuple[1]) & Q(evaluator=request.user) & Q(
                        approved=False) & Q(exercise__type=Exercise.REGULAR)).count()
            exams_reject_per_month.append(q3)
            exams_reject_qty += q3
        my_devices = request.user.my_devices
        data = {
            'exams_evaluated_per_month': exams_evaluated_per_month,
            'exams_evaluated_qty': exams_evaluated_qty,
            'exams_approved_per_month': exams_approved_per_month,
            'exams_approved_qty': exams_approved_qty,
            'exams_reject_per_month': exams_reject_per_month,
            'exams_reject_qty': exams_reject_qty,
            'users_qty': User.objects.filter(created_by=request.user).count(),
            'devices_qty': Device.objects.filter(Q(owner=request.user) | Q(admins__in=[request.user])).count(),
            'pending_exams_qty': Exam.objects.filter(
                Q(evaluator__isnull=True) & Q(device__in=my_devices)
                ).count(),
            'user_groups_qty': DeviceUsersGroup.objects.filter(created_by=request.user).count(),
        }

        return Response(data, status=200)


class RawUserDashboardReportView(APIView):

    @role_required(required_role=User.STUDENT)
    def get(self, request, months_qty=6):
        now = datetime.utcnow().replace(hour=00, minute=00, day=1, second=0, microsecond=0)

        data = {
            'news_qty': News.objects.filter(Q(created_by__in=request.user.allowed_admins)).count(),
            'new_videos_qty': Exam.objects.filter(Q(video_shares__in=[request.user]) & Q(video_views=0)).count(),
            'exams_qty': Exam.objects.filter(Q(taker=request.user) & Q(evaluator__isnull=False)).count(),
            'exercises_qty': Exercise.objects
                .filter(
                Q(type=Exercise.REGULAR) &
                Q(allowed_devices__users__in=[request.user]) &
                ~Q(exams__taker_id=request.user.id)).count()
        }

        return Response(data, status=200)


class RegisterGuestUserView(CreateAPIView):

    permission_classes = (AllowAny,)
    queryset = User.objects.filter(role=User.GUEST)
    serializer_class = WritableGuestUserSerializer


class ListUsersSharesView(ListAPIView):
    serializer_class = ReadUserSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('first_name', 'last_name', 'email')
    ordering_fields = ('id', 'first_name', 'last_name')

    def get_queryset(self):
        return User.objects.filter((Q(role=User.TEACHER) | Q(role=User.STUDENT)) & ~Q(id=self.request.user.id))

    @role_required(required_role=User.STUDENT)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
