"""Тесты для тестирования маршрутов проекта."""

# notes/tests/test_routes.py
from http import HTTPStatus

# Импортируем функцию для определения модели пользователя.
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# Импортируем класс комментария.
from notes.models import Note

# Получаем модель пользователя.
User = get_user_model()


class TestRoutes(TestCase):
    """Тесты маршрутов проекта: доступность страниц и редиректы."""

    @classmethod
    def setUpTestData(cls):
        """Тестовые данные: новость, два пользователя и заметка."""
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Другой пользователь')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст',
            slug='test-note', author=cls.author,
        )
        # Кортеж доступных автору маршрутов для 2 теста
        cls.user_urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:detail', (cls.note.slug,)),
            ('notes:edit', (cls.note.slug,)),
            ('notes:delete', (cls.note.slug,)),
            ('notes:success', None),
        )
        # Кортеж привязанных к заметке маршрутов для 2 теста
        cls.note_urls = (
            ('notes:detail', (cls.note.slug,)),
            ('notes:edit', (cls.note.slug,)),
            ('notes:delete', (cls.note.slug,)),
        )

    def test_public_pages_for_anonymous(self):
        """1R. Доступ анонима к главной странице и авторизации."""
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_availability_for_anonymous(self):
        """2R. Страница выхода доступна всем пользователям."""
        url = reverse('users:logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_access_for_logged_in_users(self):
        """3R. Доступ автора к своим заметкам (200), к чужим (404)."""
        users_statuses = (
            (self.author, HTTPStatus.OK, self.user_urls),  # все страницы
            (self.reader, HTTPStatus.NOT_FOUND, self.note_urls),  # заметки
        )
        for user, status, urls in users_statuses:
            self.client.force_login(user)
            for name, args in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects_for_anonymous(self):
        """4R. Редирект анонимного пользователя с недоступных страниц."""
        login_url = reverse('users:login')
        for name, args in self.user_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
