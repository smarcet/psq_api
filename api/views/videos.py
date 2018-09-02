from django.db.models import Q, Count
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from ..decorators import role_required
from ..exceptions import CustomValidationError
from ..models import User, Exam, ModelValidationException
from ..serializers import Exam2VideoReadSerializer, NullableExamSerializer


class VideosListAPIView(ListAPIView):
    serializer_class = Exam2VideoReadSerializer

    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('exercise__title', 'taker__first_name', 'taker__last_name', 'taker__email')
    ordering_fields = ('id',)

    def get_queryset(self):
        current_user = self.request.user
        return Exam.objects.annotate(videos_qty=Count('videos'))\
        .filter(videos_qty__gte=1).filter(
            (Q(taker=current_user) | Q(video_shares__in=[current_user]))
        ).distinct()

    @role_required(required_role=User.STUDENT)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class VideosUsersAPIView(GenericAPIView):
    queryset = Exam.objects.all()
    serializer_class = NullableExamSerializer

    @role_required(required_role=User.STUDENT)
    def put(self, request, pk, user_id):
        exam = self.get_object()
        try:
            current_user = request.user
            if not exam.taker == current_user:
                raise ModelValidationException(
                    _("User {user_id} cant share video {exam_id}").format(user_id=current_user.id,
                                                                           exam_id=pk))

            user = User.objects.get(pk=user_id)

            exam.add_share(user)

            return Response(status=status.HTTP_204_NO_CONTENT)

        except ModelValidationException as error1:
            raise CustomValidationError(str(error1), 'error')

        except User.DoesNotExist:
            raise Http404(_("User %s does not exists") % user_id)

    @role_required(required_role=User.STUDENT)
    def delete(self, request, pk, user_id):
        exam = self.get_object()
        try:
            current_user = request.user
            if not exam.taker == current_user:
                raise ModelValidationException(
                    _("User {user_id} cant share video {exam_id}").format(user_id=current_user.id,
                                                                           exam_id=pk))

            user = User.objects.get(pk=user_id)

            exam.remove_share(user)

            return Response(status=status.HTTP_204_NO_CONTENT)

        except ModelValidationException as error1:
            raise CustomValidationError(str(error1), 'error')

        except User.DoesNotExist:
            raise Http404(_("User %s does not exists") % user_id)


class VideoPlayAPIView(GenericAPIView):
    queryset = Exam.objects.all()
    serializer_class = NullableExamSerializer

    @role_required(required_role=User.STUDENT)
    def put(self, request, pk):
        exam = self.get_object()
        try:
            current_user = request.user
            if not exam.can_reproduce(current_user):
                raise ModelValidationException(
                    _("User {user_id} cant view video {exam_id}").format(user_id=current_user.id,
                                                                           exam_id=pk))

            exam.add_view()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except ModelValidationException as error1:
            raise CustomValidationError(str(error1), 'error')
