from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from users.filters import PaymentFilter
from users.models import User, Payment
from users.serializer import UserSerializer, PaymentSerializer


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

    def get_queryset(self):
        """
        Фильтруем платежи:
        - Модераторы видят ВСЕ платежи
        - Обычные пользователи видят только СВОИ платежи
        """
        user = self.request.user

        # Если пользователь модератор - показываем все платежи
        if user.groups.filter(name="Moders").exists():
            return Payment.objects.all()

        # Иначе показываем только платежи пользователя
        return Payment.objects.filter(user=user)
