from rest_framework import serializers
from ..models import FileUpload
from rest_framework.reverse import reverse


class FileUploadSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse('exams-upload-details',
                       kwargs={'pk': obj.id},
                       request=self.context['request'])

    class Meta:
        model = FileUpload
        fields = '__all__'
        read_only_fields = ('status', 'completed_at')