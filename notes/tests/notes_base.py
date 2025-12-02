from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class NotesBaseTestCase(TestCase):
    """
    Базовый класс для тестов приложения notes.

    Предоставляет:
      - создание пользователя-автора и читателя
      - фикстурную заметку с известным slug
      - URL-константы (list, add, detail, edit, delete, success)
      - данные формы для создания новой заметки
      - авторизованные и анонимный клиенты
    """

    ORIGINAL_TITLE = 'Title'
    ORIGINAL_TEXT = 'Text'
    ORIGINAL_SLUG = 'slug'

    NEW_TITLE = 'New Title Note'
    NEW_TEXT = 'New Note text'
    NEW_SLUG = 'new-title-note'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.reader = User.objects.create(username='Reader')

        cls.note = Note.objects.create(
            title=cls.ORIGINAL_TITLE,
            text=cls.ORIGINAL_TEXT,
            slug=cls.ORIGINAL_SLUG,
            author=cls.author,
        )

        cls.home_url = reverse('notes:home')
        cls.login_url = reverse('users:login')
        cls.signup_url = reverse('users:signup')
        cls.logout_url = reverse('users:logout')
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.detail_url = reverse('notes:detail', args=(cls.ORIGINAL_SLUG,))
        cls.edit_url = reverse('notes:edit', args=(cls.ORIGINAL_SLUG,))
        cls.delete_url = reverse('notes:delete', args=(cls.ORIGINAL_SLUG,))
        cls.success_url = reverse('notes:success')

        cls.form_data = {
            'title': cls.NEW_TITLE,
            'text': cls.NEW_TEXT,
            'slug': cls.NEW_SLUG,
        }

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.anonymous_client = Client()

        cls.initial_notes_count = Note.objects.count()
