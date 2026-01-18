from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, AllowAny

from users.filters import PaymentFilter
from users.models import User, Payment
from users.serializer import UserSerializer, PaymentSerializer


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

    # Фильтр по пользователю
    def get_queryset(self):
        user = self.request.user
        queryset = Payment.objects.all()

        if not user.is_staff:
            queryset = queryset.filter(user=user)

        return queryset
