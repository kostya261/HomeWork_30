from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Curse, Lesson, Subscription
from lms.paginators import CursePaginator
from lms.serializers import CurseSerializer, LessonSerializer, CurseDetailSerializer
from users.permissions import IsModer, IsOwner

import logging

logger = logging.getLogger(__name__)


class CurseViewSet(viewsets.ModelViewSet):
    serializer_class = CurseSerializer
    queryset = Curse.objects.all()
    pagination_class = CursePaginator

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
        else:
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
    pagination_class = CursePaginator

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


class SubscriptionToggleAPIView(APIView):
    """
    APIView для управления подпиской на курс.
    POST: Добавить/удалить подписку
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        from .serializers import SubscriptionToggleSerializer
        from .models import Curse

        # Валидируем входные данные
        serializer = SubscriptionToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        course_id = serializer.validated_data['course_id']

        # Получаем курс
        course = get_object_or_404(Curse, id=course_id)

        # Ищем существующую подписку
        subscription = Subscription.objects.filter(
            user=user,
            course=course
        ).first()

        # Если подписка существует - удаляем
        if subscription:
            subscription.delete()
            message = 'Подписка удалена'
            subscribed = False
        # Если подписки нет - создаем
        else:
            Subscription.objects.create(user=user, course=course)
            message = 'Подписка добавлена'
            subscribed = True

        return Response({
            "message": message,
            "subscribed": subscribed,
            "course_id": course_id,
            "course_title": course.title
        }, status=status.HTTP_200_OK)
