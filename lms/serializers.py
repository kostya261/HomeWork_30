from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from lms.models import Curse, Lesson, Subscription
from lms.validators import validate_allowed_domains, validate_text_for_links


class CurseSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Curse
        fields = '__all__'

    def get_is_subscribed(self, obj):
        """
        Проверяет, подписан ли текущий пользователь на этот курс.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Проверяем, есть ли подписка у пользователя на этот курс
            return Subscription.objects.filter(
                user=request.user,
                course=obj
            ).exists()
        return False

    def validate_description(self, value):
        """Валидация описания курса"""
        validate_text_for_links(value)
        return value


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

    # Валидация поля link_video
    link_video = serializers.URLField(
        required=False,
        allow_null=True,
        allow_blank=True,
        validators=[validate_allowed_domains]
    )

    def validate_description(self, value):
        """Валидация описания урока"""
        validate_text_for_links(value)
        return value


class CurseDetailSerializer(ModelSerializer):
    # Количество уроков
    lesson_count = serializers.SerializerMethodField()

    # Список уроков
    lessons = LessonSerializer(many=True, read_only=True, source='lesson_set')

    is_subscribed = serializers.SerializerMethodField()

    def get_lesson_count(self, curse):
        return Lesson.objects.filter(curse=curse).count()

    def get_is_subscribed(self, obj):
        """
        Проверяет, подписан ли текущий пользователь на этот курс.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                course=obj
            ).exists()
        return False

    class Meta:
        model = Curse
        fields = ['id', 'title', 'image', 'description', 'lesson_count', 'lessons', 'is_subscribed']

    def validate_description(self, value):
        """Валидация описания курса (в детальном сериализаторе)"""
        validate_text_for_links(value)
        return value


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для подписки.
    """

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'course', 'subscribed_at']
        read_only_fields = ['id', 'subscribed_at']


class SubscriptionToggleSerializer(serializers.Serializer):
    """
    Сериализатор для переключения подписки.
    Принимает только ID курса.
    """
    course_id = serializers.IntegerField(required=True)

    def validate_course_id(self, value):
        # Проверяем, что курс существует
        from .models import Curse
        try:
            Curse.objects.get(id=value)
        except Curse.DoesNotExist:
            raise serializers.ValidationError("Курс с указанным ID не существует")
        return value
