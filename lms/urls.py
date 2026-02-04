from django.urls import path
from rest_framework.routers import DefaultRouter


from lms.views import (
    CurseViewSet,
    LessonCreateAPIView,
    LessonListAPIView,
    LessonRetrieveAPIView,
    LessonUpdateAPIView,
    LessonDestroyAPIView,
    SubscriptionToggleAPIView, test_send_email_task, test_deactivate_users_task, task_status)

app_name = 'lms'  # LmsConfig.name

router = DefaultRouter()

router.register(r'curse', CurseViewSet, basename='curse')
urlpatterns = [
    path('lesson/create/', LessonCreateAPIView.as_view(), name='lesson_create'),
    path('lesson/', LessonListAPIView.as_view(), name='lesson_list'),
    path('lesson/<int:pk>/', LessonRetrieveAPIView.as_view(), name='lesson_get'),
    path('lesson/update/<int:pk>/', LessonUpdateAPIView.as_view(), name='lesson_update'),
    path('lesson/delete/<int:pk>/', LessonDestroyAPIView.as_view(), name='lesson_delete'),
    path('subscription/toggle/', SubscriptionToggleAPIView.as_view(), name='subscription_toggle'),
    # ну как то так я решил
    path('test/send-email/', test_send_email_task, name='test_send_email'),
    path('test/deactivate-users/', test_deactivate_users_task, name='test_deactivate_users'),
    path('task-status/<str:task_id>/', task_status, name='task_status'),
] + router.urls
