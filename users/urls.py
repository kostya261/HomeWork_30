from rest_framework.routers import DefaultRouter
from users.views import UserViewSet, PaymentViewSet

app_name = 'users'

router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')
router.register(r'payment', PaymentViewSet, basename='payment')

urlpatterns = [

] + router.urls
