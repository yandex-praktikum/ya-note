"""Тесты контента проекта."""

# notes/tests/test_content.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNotesList(TestCase):
    """Тесты контента проекта: страница списка заметок."""

    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        """Тестовые данные: два пользователя и пять заметок одного из них."""
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Другой пользователь')
        all_notes = [
            Note(
                title=f'Заметка {index}',
                text='Просто текст.',
                slug=f'note-{index}',
                author=cls.author,
            )
            for index in range(5)
        ]
        Note.objects.bulk_create(all_notes)

    def test_notes_count(self):
        """1C. В списке выводятся все заметки пользователя."""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        self.assertEqual(response.context['object_list'].count(), 5)

    def test_list_contains_only_own_notes(self):
        """2C. В списке не выводятся чужие заметки."""
        self.client.force_login(self.reader)
        response = self.client.get(self.LIST_URL)
        self.assertEqual(len(response.context['object_list']), 0)


class TestNoteDetail(TestCase):
    """Тесты контента проекта: страница отдельной заметки."""

    @classmethod
    def setUpTestData(cls):
        """Тестовые данные: заметка с известными значениями полей."""
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Просто текст.',
            slug='test-note',
            author=cls.author,
        )
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))

    def test_note_data_in_context(self):
        """3C. На странице заметки выводятся её заголовок, текст и автор."""
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('note', response.context)
        note = response.context['note']
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.author)

    def test_form_pages_have_note_form(self):
        """4C. На страницах добавления и редактирования есть NoteForm."""
        self.client.force_login(self.author)
        edit_url = reverse('notes:edit', args=(self.note.slug,))
        for url in (reverse('notes:add'), edit_url):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
