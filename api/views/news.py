from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from api.exceptions import CustomValidationError
from api.models import ModelValidationException
from ..decorators import role_required
from ..models import User, News
from ..serializers import ReadNewsSerializer, WriteNewsSerializer
from django.utils.translation import ugettext_lazy as _


class NewsListCreateAPIView(ListCreateAPIView):
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('title', 'body')
    ordering_fields = ('id', 'title', 'created')

    def get_queryset(self):
        current_user = self.request.user
        if current_user.role == User.TEACHER:
            return News.objects.filter(created_by=self.request.user)
        return News.objects.filter(created_by__in=current_user.allowed_admins)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WriteNewsSerializer
        return ReadNewsSerializer

    @role_required(required_role=User.STUDENT)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @role_required(required_role=User.TEACHER)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class NewsRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = News.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return WriteNewsSerializer
        return ReadNewsSerializer

    def patch(self, request, *args, **kwargs):
        pass

    @role_required(required_role=User.STUDENT)
    def get(self, request, *args, **kwargs):
        try:
            news = self.get_object()
            current_user = request.user
            if current_user.role == User.STUDENT and news.created_by not in current_user.allowed_admins:
                # exam should be own by user
                raise ModelValidationException(
                    _("news {news_id} does not belongs to user {user_id}").format(user_id=current_user.id,
                                                                                  exam_id=news.id))
            return self.retrieve(request, *args, **kwargs)

        except ModelValidationException as error1:
            raise CustomValidationError(str(error1))

    @role_required(required_role=User.TEACHER)
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    @role_required(required_role=User.TEACHER)
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
