from celery.result import AsyncResult
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Curse, Lesson, Subscription
from lms.paginators import CursePaginator
from lms.serializers import CurseSerializer, LessonSerializer, CurseDetailSerializer
from users.permissions import IsModer, IsOwner

from .tasks import send_course_update_email, send_lesson_update_email, deactivate_inactive_users

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

        if getattr(self, 'swagger_fake_view', False):
            return Curse.objects.none()

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

    def perform_update(self, serializer):
        """Сохраняет изменения и запускает рассылку уведомлений"""
        instance = serializer.save()

        send_course_update_email.delay(instance.id)

        logger.info(f"Курс {instance.title} обновлен. Задача на рассылку запущена.")


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

        if getattr(self, 'swagger_fake_view', False):
            return Lesson.objects.none()

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
        """ Фильтруем queryset так же как в LessonListAPIView """
        user = self.request.user

        if getattr(self, 'swagger_fake_view', False):
            return Lesson.objects.none()

        if user.groups.filter(name="Moders").exists():
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=user)


class LessonUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsModer | IsOwner, IsAuthenticated]

    def get_queryset(self):
        """ Фильтруем queryset так же как в LessonListAPIView """
        user = self.request.user

        if getattr(self, 'swagger_fake_view', False):
            return Lesson.objects.none()

        if user.groups.filter(name="Moders").exists():
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=user)

    def perform_update(self, serializer):
        """Сохраняет изменения и запускает рассылку уведомлений"""
        instance = serializer.save()

        send_lesson_update_email.delay(instance.id)

        logger.info(f"Урок {instance.title} обновлен. Задача на проверку и рассылку запущена.")


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, ~IsModer, IsOwner]

    def get_queryset(self):
        """ Фильтруем queryset так же как в LessonListAPIView """
        user = self.request.user

        if getattr(self, 'swagger_fake_view', False):
            return Lesson.objects.none()

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


# ----------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAdminUser])  # Только админы могут запускать тесты
def test_send_email_task(request):
    """
    Тестовый эндпоинт для запуска задачи рассылки email.
    Нужно передать course_id в теле запроса.
    """
    course_id = request.data.get('course_id')

    if not course_id:
        return Response(
            {'error': 'Не указан course_id'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Запускаем задачу асинхронно
        task = send_course_update_email.delay(course_id)

        return Response({
            'message': 'Задача на рассылку email запущена',
            'task_id': task.id,
            'course_id': course_id,
            'status_url': f'http://localhost:8000/api/task-status/{task.id}/'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': f'Ошибка: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAdminUser])
def test_deactivate_users_task(request):
    """
    Тестовый эндпоинт для запуска задачи блокировки неактивных пользователей.
    """
    try:
        # Запускаем задачу асинхронно
        task = deactivate_inactive_users.delay()

        return Response({
            'message': 'Задача на блокировку неактивных пользователей запущена',
            'task_id': task.id,
            'status_url': f'http://localhost:8000/api/task-status/{task.id}/'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': f'Ошибка: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_status(request, task_id):
    """
    Проверка статуса задачи Celery.
    """
    try:
        task_result = AsyncResult(task_id)

        response_data = {
            'task_id': task_id,
            'status': task_result.status,
            'ready': task_result.ready(),
        }

        if task_result.ready():
            response_data['result'] = task_result.result
            if task_result.failed():
                response_data['error'] = str(task_result.result)

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': f'Ошибка: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
