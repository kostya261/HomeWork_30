from django.contrib.auth.models import Group
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from users.models import User
from .models import Curse, Lesson, Subscription


class LMSTestCase(APITestCase):
    """
    Базовый класс для тестов LMS.
    """

    def setUp(self):
        """
        Подготовка данных перед каждым тестом.
        """
        # Создаем пользователей
        self.user_owner = User.objects.create(
            email='owner@test.com',
            password='testpass123'
        )
        self.user_moder = User.objects.create(
            email='moder@test.com',
            password='testpass123'
        )
        self.user_other = User.objects.create(
            email='other@test.com',
            password='testpass123'
        )

        # Создаем группу модераторов и добавляем пользователя
        moder_group, _ = Group.objects.get_or_create(name='Moders')
        self.user_moder.groups.add(moder_group)

        # Создаем курс
        self.course = Curse.objects.create(
            title='Тестовый курс',
            description='Описание тестового курса',
            owner=self.user_owner
        )

        # Создаем урок
        self.lesson = Lesson.objects.create(
            title='Тестовый урок',
            description='Описание тестового урока',
            link_video='https://www.youtube.com/watch?v=test123',
            curse=self.course,
            owner=self.user_owner
        )

        # URL для тестов
        self.lesson_list_url = reverse('lms:lesson_list')
        self.lesson_detail_url = reverse('lms:lesson_get', kwargs={'pk': self.lesson.pk})
        self.lesson_create_url = reverse('lms:lesson_create')
        self.lesson_update_url = reverse('lms:lesson_update', kwargs={'pk': self.lesson.pk})
        self.lesson_delete_url = reverse('lms:lesson_delete', kwargs={'pk': self.lesson.pk})

        self.subscription_toggle_url = reverse('lms:subscription_toggle')


class LessonCRUDTests(LMSTestCase):
    """
    Тесты CRUD операций для уроков.
    """

    def test_lesson_list_authenticated(self):
        """Тест получения списка уроков (аутентифицированный пользователь)"""
        self.client.force_authenticate(user=self.user_owner)
        response = self.client.get(self.lesson_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_lesson_list_unauthenticated(self):
        """Тест получения списка уроков (неаутентифицированный)"""
        response = self.client.get(self.lesson_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lesson_create_by_owner(self):
        """Тест создания урока владельцем"""
        self.client.force_authenticate(user=self.user_owner)
        data = {
            'title': 'Новый урок',
            'description': 'Описание нового урока',
            'link_video': 'https://www.youtube.com/watch?v=new123',
            'curse': self.course.id,
        }
        response = self.client.post(self.lesson_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_lesson_create_by_moderator(self):
        """Тест создания урока модератором (403 Forbidden)"""
        self.client.force_authenticate(user=self.user_moder)
        data = {
            'title': 'Урок от модератора',
            'description': 'Описание',
            'link_video': 'https://youtube.com/watch?v=moder',
            'curse': self.course.id,
        }
        response = self.client.post(self.lesson_create_url, data)
        # Модераторы не могут создавать уроки: 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_retrieve_by_owner(self):
        """Тест получения урока владельцем"""
        self.client.force_authenticate(user=self.user_owner)
        response = self.client.get(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Тестовый урок')

    def test_lesson_retrieve_by_moderator(self):
        """Тест получения урока модератором"""
        self.client.force_authenticate(user=self.user_moder)
        response = self.client.get(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_retrieve_by_other_user(self):
        """Тест получения урока другим пользователем (должна быть ошибка)"""
        self.client.force_authenticate(user=self.user_other)
        response = self.client.get(self.lesson_detail_url)
        # Другой пользователь не должен видеть чужой урок
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_lesson_update_by_owner(self):
        """Тест обновления урока владельцем"""
        self.client.force_authenticate(user=self.user_owner)
        data = {
            'title': 'Обновленный урок',
            'description': 'Обновленное описание',
            'link_video': 'https://youtube.com/watch?v=updated',
        }
        response = self.client.patch(self.lesson_update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Обновленный урок')

    def test_lesson_update_by_moderator(self):
        """Тест обновления урока модератором"""
        self.client.force_authenticate(user=self.user_moder)
        data = {'title': 'Обновлено модератором'}
        response = self.client.patch(self.lesson_update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_update_by_other_user(self):
        """Тест обновления урока другим пользователем (должна быть ошибка)"""
        self.client.force_authenticate(user=self.user_other)
        data = {'title': 'Попытка изменения'}
        response = self.client.patch(self.lesson_update_url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_lesson_delete_by_moderator(self):
        """Тест удаления урока модератором (403 Forbidden)"""
        self.client.force_authenticate(user=self.user_moder)
        response = self.client.delete(self.lesson_delete_url)
        # Модераторы не могут удалять уроки: 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_delete_by_other_user(self):
        """Тест удаления урока другим пользователем (должна быть ошибка)"""
        self.client.force_authenticate(user=self.user_other)
        response = self.client.delete(self.lesson_delete_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_lesson_create_with_invalid_link(self):
        """Тест создания урока с запрещенной ссылкой"""
        self.client.force_authenticate(user=self.user_owner)
        data = {
            'title': 'Урок с плохой ссылкой',
            'description': 'Описание',
            'link_video': 'https://vk.com/video123',  # Не YouTube!
            'curse': self.course.id,
        }
        response = self.client.post(self.lesson_create_url, data)
        # Должна быть ошибка валидации
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('link_video', response.data)


class SubscriptionTests(LMSTestCase):
    """
    Тесты функционала подписок.
    """

    def test_subscription_add(self):
        """Тест добавления подписки"""
        self.client.force_authenticate(user=self.user_owner)
        data = {'course_id': self.course.id}

        response = self.client.post(self.subscription_toggle_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(response.data['subscribed'])

        # Проверяем, что подписка создалась в БД
        subscription_exists = Subscription.objects.filter(
            user=self.user_owner,
            course=self.course
        ).exists()
        self.assertTrue(subscription_exists)

    def test_subscription_remove(self):
        """Тест удаления подписки"""
        # Сначала создаем подписку
        Subscription.objects.create(user=self.user_owner, course=self.course)

        self.client.force_authenticate(user=self.user_owner)
        data = {'course_id': self.course.id}

        response = self.client.post(self.subscription_toggle_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertFalse(response.data['subscribed'])

        # Проверяем, что подписка удалилась из БД
        subscription_exists = Subscription.objects.filter(
            user=self.user_owner,
            course=self.course
        ).exists()
        self.assertFalse(subscription_exists)

    def test_subscription_toggle_twice(self):
        """Тест переключения подписки дважды (добавить → удалить)"""
        self.client.force_authenticate(user=self.user_owner)
        data = {'course_id': self.course.id}

        # Первый запрос - добавляем
        response1 = self.client.post(self.subscription_toggle_url, data)
        self.assertTrue(response1.data['subscribed'])

        # Второй запрос - удаляем
        response2 = self.client.post(self.subscription_toggle_url, data)
        self.assertFalse(response2.data['subscribed'])

    def test_subscription_with_invalid_course(self):
        """Тест подписки на несуществующий курс - 400 Bad Request"""
        self.client.force_authenticate(user=self.user_owner)
        data = {'course_id': 99999}

        response = self.client.post(self.subscription_toggle_url, data)
        # Сериализатор возвращает 400 при ValidationError
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscription_field_in_course(self):
        """Тест поля is_subscribed в данных курса"""
        # Создаем подписку
        Subscription.objects.create(user=self.user_owner, course=self.course)

        self.client.force_authenticate(user=self.user_owner)

        # Получаем детальную информацию о курсе
        curse_detail_url = reverse('lms:curse-detail', kwargs={'pk': self.course.pk})
        response = self.client.get(curse_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_subscribed', response.data)
        self.assertTrue(response.data['is_subscribed'])

    def test_subscription_unauthenticated(self):
        """Тест подписки без аутентификации"""
        data = {'course_id': self.course.id}
        response = self.client.post(self.subscription_toggle_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PaginationTests(LMSTestCase):
    """
    Тесты пагинации.
    """

    def setUp(self):
        """Дополнительная настройка для тестов пагинации"""
        super().setUp()

        # Создаем дополнительные уроки для теста пагинации
        for i in range(15):
            Lesson.objects.create(
                title=f'Урок для пагинации {i}',
                description=f'Описание урока {i}',
                link_video=f'https://youtube.com/watch?v=page{i}',
                curse=self.course,
                owner=self.user_owner
            )

    def test_lesson_pagination_default(self):
        """Тест пагинации уроков (у тебя page_size=5)"""
        self.client.force_authenticate(user=self.user_owner)
        response = self.client.get(self.lesson_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 16)
        self.assertEqual(len(response.data['results']), 5)

    def test_lesson_pagination_custom_page_size(self):
        """Тест пагинации с указанием page_size"""
        self.client.force_authenticate(user=self.user_owner)
        response = self.client.get(f'{self.lesson_list_url}?page_size=5')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)

    def test_lesson_pagination_max_page_size(self):
        """Тест ограничения максимального page_size"""
        self.client.force_authenticate(user=self.user_owner)
        # Запрашиваем 100, но максимум 50 (должно ограничиться)
        response = self.client.get(f'{self.lesson_list_url}?page_size=100')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data['results']), 50)
