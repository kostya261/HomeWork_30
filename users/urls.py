from django.http import HttpResponse
from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views import UserViewSet, PaymentViewSet, UserCreateAPIView

app_name = 'users'

router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')
router.register(r'payment', PaymentViewSet, basename='payment')

urlpatterns = [
    path('register/', UserCreateAPIView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(permission_classes=(AllowAny,)), name='token_refresh'),
    path('payment/success/', lambda request: HttpResponse('Оплата успешна!'), name='payment_success'),
    path('payment/cancel/', lambda request: HttpResponse('Оплата отменена'), name='payment_cancel'),
] + router.urls
