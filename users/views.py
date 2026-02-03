from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status, serializers
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from users.filters import PaymentFilter
from users.models import User, Payment
from users.serializer import UserSerializer, PaymentSerializer
from users.services import convert_rub_to_dollars, create_stripe_price, create_stripe_product, create_stripe_session, \
    get_stripe_session_status


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        serializer.save(is_active=True)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        """Разрешаем регистрацию без аутентификации"""
        if self.action == 'create':
            return [AllowAny()]  # Регистрация доступна всем
        return [IsAuthenticated()]  # Остальные действия требуют входа


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PaymentFilter

    def perform_create(self, serializer):
        # Сохраняем платеж
        payment = serializer.save(user=self.request.user)

        try:
            # Определяем, что оплачивается: курс или урок
            if payment.paid_course:
                product_name = f"Курс: {payment.paid_course.title}"
                product_description = payment.paid_course.description
            else:
                product_name = f"Урок: {payment.paid_lesson.title}"
                product_description = payment.paid_lesson.description

            # 1. Конвертируем сумму в центы USD
            amount_cents = convert_rub_to_dollars(payment.amount)

            # 2. Создаем продукт в Stripe
            product_id = create_stripe_product(
                name=product_name,
                description=product_description[:500] if product_description else None
            )

            # 3. Создаем цену в Stripe
            price_id = create_stripe_price(
                amount_cents=amount_cents,
                product_id=product_id
            )

            # 4. Создаем сессию оплаты
            session_data = create_stripe_session(price_id)

            # 5. Сохраняем данные Stripe в платеж
            payment.stripe_session_id = session_data['session_id']
            payment.stripe_price_id = price_id
            payment.link_payment = session_data['url']
            payment.status = 'pending'
            payment.save()

        except Exception as e:
            # В случае ошибки удаляем созданный платеж
            payment.delete()
            raise serializers.ValidationError(f"Ошибка создания платежа: {str(e)}")

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """ Проверка статуса платежа. """
        payment = self.get_object()

        if not payment.stripe_session_id:
            return Response(
                {'error': 'Нет данных о сессии оплаты'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            status_stripe = get_stripe_session_status(payment.stripe_session_id)

            # Обновляем статус в базе данных
            if status_stripe == 'paid' and payment.status != 'paid':
                payment.status = 'paid'
                payment.save()

            return Response({
                'payment_id': payment.id,
                'stripe_status': status_stripe,
                'internal_status': payment.status,
                'amount': payment.amount,
                'paid_for': payment.paid_course.title if payment.paid_course else payment.paid_lesson.title
            })

        except Exception as e:
            return Response(
                {'error': f'Ошибка при проверке статуса: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_queryset(self):
        """
        Фильтруем платежи:
        - Модераторы видят ВСЕ платежи
        - Обычные пользователи видят только СВОИ платежи
        """
        user = self.request.user

        if getattr(self, 'swagger_fake_view', False):
            return Payment.objects.none()

        # Если пользователь модератор - показываем все платежи
        if user.groups.filter(name="Moders").exists():
            return Payment.objects.all()

        # Иначе показываем только платежи пользователя
        return Payment.objects.filter(user=user)
