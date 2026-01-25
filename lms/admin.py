from django.contrib import admin
from .models import Curse, Lesson


@admin.register(Curse)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'id')
    list_filter = ('owner',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'curse', 'owner', 'id')
    list_filter = ('curse', 'owner')
