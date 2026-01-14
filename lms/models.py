from django.db import models


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

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
