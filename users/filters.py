import django_filters
from users.models import Payment


class PaymentFilter(django_filters.FilterSet):
    # Фильтр по курсу (по ID)
    course = django_filters.NumberFilter(field_name='paid_course', lookup_expr='exact')

    # Фильтр по уроку (по ID)
    lesson = django_filters.NumberFilter(field_name='paid_lesson', lookup_expr='exact')

    # Фильтр по способу оплаты
    payment_method = django_filters.ChoiceFilter(choices=Payment.PAYMENT_METHODS)

    # Сортировка по дате
    ordering = django_filters.OrderingFilter(
        fields=(
            ('payment_date', 'date'),  # 'date' для asc, '-date' для desc
        ),
        field_labels={
            'payment_date': 'Дата оплаты',
        }
    )

    # Фильтр по курсу через урок
    lesson_in_course = django_filters.NumberFilter(
        field_name='paid_lesson__curse',
        lookup_expr='exact',
        label='Курс (через урок)'
    )

    class Meta:
        model = Payment
        fields = ['course', 'lesson', 'payment_method']
