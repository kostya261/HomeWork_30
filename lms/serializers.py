from rest_framework import serializers

from lms.models import Curse, Lesson


class CurseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curse
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
