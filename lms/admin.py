from django.contrib import admin
from .models import Curse, Lesson, Subscription


@admin.register(Curse)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'id')
    list_filter = ('owner',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'curse', 'owner', 'id')
    list_filter = ('curse', 'owner')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'subscribed_at')
    list_filter = ('course', 'subscribed_at')
    search_fields = ('user__email', 'course__title')
