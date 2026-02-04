import os
import django

from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


def create_periodic_task():
    """Создает периодическую задачу для блокировки неактивных пользователей"""

    # Создаем расписание: каждый день в 3:00 утра
    schedule, created = CrontabSchedule.objects.get_or_create(
        minute='0',
        hour='3',
        day_of_week='*',
        day_of_month='*',
        month_of_year='*',
        timezone=timezone.get_current_timezone()
    )

    if created:
        print("Расписание создано: каждый день в 3:00")

    # Создаем или обновляем задачу
    task, task_created = PeriodicTask.objects.get_or_create(
        name='Блокировка неактивных пользователей',
        defaults={
            'task': 'lms.tasks.deactivate_inactive_users',
            'crontab': schedule,
            'enabled': True,
            'description': 'Автоматически блокирует пользователей, которые не заходили более месяца',
        }
    )

    if task_created:
        print("✅ Периодическая задача создана!")
        print(f"   Задача: {task.name}")
        print("   Расписание: каждый день в 3:00")
        print(f"   Функция: {task.task}")
    else:
        # Обновляем существующую задачу
        task.crontab = schedule
        task.enabled = True
        task.save()
        print("✅ Существующая задача обновлена!")

    return task


if __name__ == '__main__':
    create_periodic_task()
