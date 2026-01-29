from django.db import models

from users.models import User


class Curse(models.Model):
    title = models.CharField(
        max_length=150,
        verbose_name='Название курса',
        help_text="Укажите название курса"
    )

    image = models.ImageField(
        upload_to='image/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Загрузите изображение',
        help_text='Загрузите изображение'
    )

    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True,
        help_text='Введите описание'
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Владелец',
        help_text='Укажите владельца')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'


class Lesson(models.Model):
    title = models.CharField(
        max_length=150,
        verbose_name='Название урока',
        help_text="Укажите название Урока"
    )

    preview = models.ImageField(
        upload_to='image/%Y/%m/%d/',
        verbose_name='Загрузите изображение',
        help_text='Загрузите изображение',
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание',
        help_text='Введите описание'
    )

    link_video = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Ссылка на видео'
    )

    curse = models.ForeignKey(
        Curse,
        on_delete=models.SET_NULL,
        verbose_name='Курс',
        help_text='Выберите курс',
        blank=True,
        null=True
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name='Владелец',
        help_text='Укажите владельца')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['id']


class Subscription(models.Model):
    """
    Модель подписки пользователя на курс.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='subscriptions'
    )

    course = models.ForeignKey(
        Curse,
        on_delete=models.CASCADE,
        verbose_name='Курс',
        related_name='subscriptions'
    )

    # Дата подписки
    subscribed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата подписки'
    )

    # Уникальная пара пользователь-курс (один пользователь - одна подписка на курс)
    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ['user', 'course']  # Важно!
        ordering = ['-subscribed_at']

    def __str__(self):
        return f'{self.user.email} подписан на {self.course.title}'
