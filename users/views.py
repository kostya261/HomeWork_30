from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from users.models import User
from users.serializer import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        """Разрешаем регистрацию без аутентификации"""
        if self.action == 'create':
            return [AllowAny()]  # Регистрация доступна всем
        return [IsAuthenticated()]  # Остальные действия требуют входа
