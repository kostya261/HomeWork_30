
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'phone', 'city', 'avatar', 'first_name', 'last_name', 'is_active',
                  'date_joined']
        read_only_fields = ['id', 'is_active', 'date_joined']

    def create(self, validated_data):
        # Хэшируем пароль
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
