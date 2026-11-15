"""Тесты логики проекта."""

# notes/tests/test_logic.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

# Если в notes/forms.py есть константы стоп-слов и предупреждения —
# импортируйте их. Названия сверьте со своим файлом форм!
from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    """Тестирование создания заметок."""

    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст заметки'

    @classmethod
    def setUpTestData(cls):
        """Тестовые данные: пользователь и заметка для проверки слага."""
        cls.add_url = reverse('notes:add')
        cls.user = User.objects.create(username='Пользователь')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        # Заметка с известным слагом — её наличие проверяет тест уникальности.
        cls.existing_note_slug = 'existing-note'
        cls.existing_note = Note.objects.create(
            title='Существующая заметка',
            text='Текст',
            slug=cls.existing_note_slug,
            author=cls.user,
        )
        # Данные для успешного создания: слаг гарантированно уникальный.
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': 'fresh-new-slug',
        }
        cls.success_url = reverse('notes:success')

    def test_anonymous_user_cant_create_note(self):
        """1L. Анонимный пользователь не может создать заметку."""
        self.client.post(self.add_url, data=self.form_data)
        # Одна заметка уже есть в фикстуре — она и должна остаться
        # единственной.
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_can_create_note(self):
        """2L. Залогиненный пользователь может создать заметку."""
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        # Была одна заметка из фикстуры, стало две.
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)
        # Новую заметку получаем по слагу — она уникальна.
        note = Note.objects.get(slug='fresh-new-slug')
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.user)

    def test_user_cant_create_note_with_duplicate_slug(self):
        """3L. Нельзя создать заметку с уже существующим слагом."""
        bad_words_data = {
            'title': self.NOTE_TITLE,
            'text': self.NOTE_TEXT,
            'slug': self.existing_note_slug,  # слаг заметки из фикстуры
        }
        response = self.auth_client.post(self.add_url, data=bad_words_data)
        form = response.context['form']
        self.assertFormError(
            form=form,
            field='slug',
            errors=self.existing_note_slug + WARNING,
        )
        # Заметка не создана: в базе по-прежнему одна.
        self.assertEqual(Note.objects.count(), 1)

    def test_slug_auto_filled_from_title(self):
        """4L. При пустом слаге он генерируется из заголовка."""
        data_without_slug = {
            'title': self.NOTE_TITLE,
            'text': self.NOTE_TEXT,
        }
        response = self.auth_client.post(self.add_url, data=data_without_slug)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.get(slug=slugify(self.NOTE_TITLE))
        self.assertEqual(new_note.title, self.NOTE_TITLE)
        self.assertEqual(new_note.text, self.NOTE_TEXT)
        self.assertEqual(new_note.author, self.user)


class TestNoteEditDelete(TestCase):
    """Тестирование редактирования и удаления заметки."""

    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TITLE = 'Новый заголовок'
    NEW_NOTE_TEXT = 'Новый текст заметки'

    @classmethod
    def setUpTestData(cls):
        """Тестовые данные: два пользователя, заметка, клиенты и адреса."""
        cls.success_url = reverse('notes:success')
        # Автор и его клиент.
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        # Читатель и его клиент.
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        # Заметка автора.
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug='test-note',
            author=cls.author,
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        # Данные для редактирования: слаг оставляем прежним.
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': 'test-note',
        }

    def test_author_can_delete_note(self):
        """5L. Автор может удалить свою заметку."""
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, self.success_url)
        # Убеждаемся, что заметка исчезла из базы.
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        """6L. Пользователь не может удалить чужую заметку."""
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Заметка по-прежнему на месте.
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """7L. Редактировать заметку может только её автор."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        # Обновляем объект из базы и проверяем новые значения.
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.slug, 'test-note')

    def test_user_cant_edit_note_of_another_user(self):
        """8L. Редактирование недоступно другому пользователю."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        # Текст и заголовок остались прежними.
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
