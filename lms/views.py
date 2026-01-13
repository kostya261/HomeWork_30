from rest_framework import viewsets, generics

from lms.models import Curse, Lesson
from lms.serializers import CurseSerializer, LessonSerializer


class CurseViewSet(viewsets.ModelViewSet):
    serializer_class = CurseSerializer
    queryset = Curse.objects.all()


class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()


class LessonUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()


class LessonDestroyAPIView(generics.DestroyAPIView):

    queryset = Lesson.objects.all()
