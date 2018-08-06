from django.db.models import Q, Count
from rest_framework.generics import ListAPIView
from ..serializers import Exam2VideoReadSerializer
from ..decorators import role_required
from ..models import User, Exam


class VideosListAPIView(ListAPIView):
    serializer_class = Exam2VideoReadSerializer

    def get_queryset(self):
        current_user = self.request.user
        return Exam.objects.annotate(videos_qty=Count('videos'))\
        .filter(videos_qty__gte=1).filter(
            (Q(taker=current_user) | Q(video_shares__in=[current_user]))
        ).distinct()

    @role_required(required_role=User.STUDENT)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
