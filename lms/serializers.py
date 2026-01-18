from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from lms.models import Curse, Lesson


class CurseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curse
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class CurseDetailSerializer(ModelSerializer):
    # Поле 1: количество уроков
    lesson_count = serializers.SerializerMethodField()

    # Поле 2: список уроков
    lessons = LessonSerializer(many=True, read_only=True, source='lesson_set')

    def get_lesson_count(self, curse):
        return Lesson.objects.filter(curse=curse).count()

    class Meta:
        model = Curse
        fields = ['id', 'title', 'image', 'description', 'lesson_count', 'lessons']
