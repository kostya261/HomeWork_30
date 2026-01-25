from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated

from lms.models import Curse, Lesson
from lms.serializers import CurseSerializer, LessonSerializer, CurseDetailSerializer
from users.permissions import IsModer, IsOwner

import logging

logger = logging.getLogger(__name__)


class CurseViewSet(viewsets.ModelViewSet):
    serializer_class = CurseSerializer
    queryset = Curse.objects.all()

    def get_queryset(self):
        """
        Фильтруем курсы:
        - Модераторы видят ВСЕ курсы
        - Обычные пользователи видят только СВОИ курсы
        """
        user = self.request.user

        # Если пользователь модератор - показываем все курсы
        if user.groups.filter(name="Moders").exists():
            return Curse.objects.all()

        # Иначе показываем только курсы владельца
        return Curse.objects.filter(owner=user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CurseDetailSerializer
        return CurseSerializer

    def perform_create(self, serializer):
        """Автоматически назначаем владельца"""
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated, ~IsModer]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsModer | IsOwner]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, ~IsModer, IsOwner]
        else:  # list, retrieve
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [~IsModer, IsAuthenticated]

    def perform_create(self, serializer):
        """Автоматически назначаем владельца"""
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Фильтруем уроки:
        - Модераторы видят ВСЕ уроки
        - Обычные пользователи видят только СВОИ уроки
         """
        user = self.request.user

        # Если пользователь модератор - показываем все уроки
        if user.groups.filter(name="Moders").exists():
            return Lesson.objects.all()

        # Иначе показываем только уроки владельца
        return Lesson.objects.filter(owner=user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsModer | IsOwner, IsAuthenticated]

    def get_queryset(self):
        """Фильтруем queryset так же как в LessonListAPIView"""
        user = self.request.user

        if user.groups.filter(name="Moders").exists():
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=user)


class LessonUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsModer | IsOwner, IsAuthenticated]

    def get_queryset(self):
        """Фильтруем queryset так же как в LessonListAPIView"""
        user = self.request.user

        if user.groups.filter(name="Moders").exists():
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=user)


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, ~IsModer, IsOwner]

    def get_queryset(self):
        """Фильтруем queryset так же как в LessonListAPIView"""
        user = self.request.user

        if user.groups.filter(name="Moders").exists():
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=user)
