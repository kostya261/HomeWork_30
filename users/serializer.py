from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from users.models import User, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    # История платежей пользователя
    payment_history = PaymentSerializer(many=True, read_only=True, source='payments')

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'phone', 'city', 'avatar', 'first_name', 'last_name', 'is_active',
                  'date_joined', 'payment_history']
        read_only_fields = ['id', 'is_active', 'date_joined']

    def create(self, validated_data):
        # Хэшируем пароль
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
