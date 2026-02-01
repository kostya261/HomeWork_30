from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None

    email = models.EmailField(
        unique=True, verbose_name="Почта", help_text="Укажите почту"
    )

    phone = models.CharField(
        max_length=35,
        blank=True,
        null=True,
        verbose_name="Телефон",
        help_text="Укажите телефон",
    )
    city = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Город",
        help_text="Укажите город",
    )
    avatar = models.ImageField(
        upload_to="users/avatars",
        blank=True,
        null=True,
        verbose_name="Avatar",
        help_text="Загрузите аватар",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Payment(models.Model):
    # Способы оплаты
    PAYMENT_CASH = 'cash'
    PAYMENT_TRANSFER = 'transfer'

    PAYMENT_METHODS = [
        (PAYMENT_CASH, 'Наличные'),
        (PAYMENT_TRANSFER, 'Перевод на счет'),
    ]

    # Связи
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='payments',
        help_text='Укажите пользователя'
    )

    # Оплаченный курс (может быть null если оплачен урок)
    paid_course = models.ForeignKey(
        'lms.Curse',  # Ссылка на модель из другого приложения
        on_delete=models.SET_NULL,
        verbose_name='Оплаченный курс',
        null=True,
        blank=True,
        related_name='payments'
    )

    # Оплаченный урок (может быть null если оплачен курс)
    paid_lesson = models.ForeignKey(
        'lms.Lesson',  # Ссылка на модель из другого приложения
        on_delete=models.SET_NULL,
        verbose_name='Оплаченный урок',
        null=True,
        blank=True,
        related_name='payments'
    )

    # Поля оплаты
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма оплаты',
        help_text='Укажите сумму оплаты'
    )

    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата оплаты'
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        verbose_name='Способ оплаты'
    )

    link_payment = models.URLField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name='Ссылка на оплату',
        help_text='Укажите ссылку на оплату'
    )

    # Поля для Stripe
    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='ID сессии Stripe'
    )

    stripe_price_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='ID цены Stripe'
    )

    status = models.CharField(
        max_length=50,
        default='pending',
        verbose_name='Статус оплаты',
        choices=[
            ('pending', 'Ожидает оплаты'),
            ('paid', 'Оплачено'),
            ('canceled', 'Отменено'),
        ]
    )

    # Валидация: оплачен либо курс, либо урок
    def clean(self):
        if self.paid_course and self.paid_lesson:
            raise ValidationError('Оплата может быть только за курс ИЛИ за урок')
        if not self.paid_course and not self.paid_lesson:
            raise ValidationError('Укажите либо курс, либо урок для оплаты')

    def __str__(self):
        what_paid = self.paid_course.title if self.paid_course else self.paid_lesson.title
        return f'{self.user.email} - {what_paid} - {self.amount}'

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']
