from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Curse, Subscription

from datetime import timedelta
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def send_course_update_email(course_id, updated_lesson_title=None):
    """
    Отправляет email всем подписанным пользователям об обновлении курса.
    """
    try:
        course = Curse.objects.get(id=course_id)
        subscribers = Subscription.objects.filter(course=course).select_related('user')

        if not subscribers:
            logger.info(f"У курса {course.title} нет подписчиков.")
            return

        subject = f'Обновление курса: {course.title}'

        # Формируем сообщение
        if updated_lesson_title:
            message = f'В курсе "{course.title}" обновлен урок: {updated_lesson_title}.\n'
        else:
            message = f'В курсе "{course.title}" произошли обновления.\n'

        message += f'Перейти к курсу: http://localhost:8000/course/{course.id}/'

        recipient_list = [sub.user.email for sub in subscribers if sub.user.email]

        # Отправка email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )

        logger.info(f"Уведомления отправлены {len(recipient_list)} подписчикам курса '{course.title}'")

    except Curse.DoesNotExist:
        logger.error(f"Курс с id {course_id} не найден")
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомлений: {e}")


@shared_task
def send_lesson_update_email(lesson_id):
    """
    Отправляет уведомление об обновлении урока, если курс не обновлялся >4 часов.
    """
    try:
        from .models import Lesson
        lesson = Lesson.objects.get(id=lesson_id)
        course = lesson.curse

        # Проверяем, когда курс обновлялся последний раз
        four_hours_ago = timezone.now() - timedelta(hours=4)

        # Если курс обновлялся менее 4 часов назад - не отправляем
        recent_updates = Lesson.objects.filter(
            curse=course,
            updated_at__gte=four_hours_ago
        ).exists()

        if recent_updates:
            logger.info(f"Курс {course.title} обновлялся менее 4 часов назад. Уведомление не отправляется.")
            return

        # Запускаем рассылку
        send_course_update_email.delay(course.id, lesson.title)

    except Lesson.DoesNotExist:
        logger.error(f"Урок с id {lesson_id} не найден")
    except Exception as e:
        logger.error(f"Ошибка при обработке обновления урока: {e}")


@shared_task
def deactivate_inactive_users():
    """
    Блокирует пользователей, которые не заходили более месяца.
    """
    try:
        month_ago = timezone.now() - timedelta(days=30)

        # Находим активных пользователей, которые не заходили более месяца
        inactive_users = User.objects.filter(
            is_active=True,
            last_login__lt=month_ago
        )

        count = inactive_users.count()

        if count > 0:
            # Блокируем пользователей
            inactive_users.update(is_active=False)
            logger.info(f"Заблокировано {count} неактивных пользователей.")
            return f"Заблокировано {count} пользователей."
        else:
            logger.info("Неактивных пользователей для блокировки не найдено.")
            return "Нет пользователей для блокировки."

    except Exception as e:
        logger.error(f"Ошибка при блокировке неактивных пользователей: {e}")
        return f"Ошибка: {str(e)}"


@shared_task
def add():
    print("Привет")
