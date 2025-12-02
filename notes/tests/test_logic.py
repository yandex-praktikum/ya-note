from http import HTTPStatus

from pytils.translit import slugify as py_slugify

from notes.forms import WARNING
from notes.models import Note
from .notes_base import NotesBaseTestCase


class TestNoteCreation(NotesBaseTestCase):

    def test_author_can_create_note(self):
        Note.objects.all().delete()
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cannot_create_note(self):
        self.client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.initial_notes_count)

    def test_not_unique_slug(self):
        self.form_data['slug'] = self.ORIGINAL_SLUG
        response = self.author_client.post(
            self.add_url, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form = response.context['form']
        self.assertFormError(form, 'slug', self.ORIGINAL_SLUG + WARNING)
        self.assertEqual(Note.objects.count(), self.initial_notes_count)

    def test_empty_slug(self):
        Note.objects.all().delete()
        self.form_data.pop('slug')
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = py_slugify(new_note.title)
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.initial_notes_count - 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, self.NEW_TITLE)
        self.assertEqual(note.text, self.NEW_TEXT)
        self.assertEqual(note.slug, self.NEW_SLUG)
        self.assertEqual(note.author, self.author)

    def test_reader_cannot_delete_authors_note(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.initial_notes_count)

    def test_other_user_cant_edit_note(self):
        response = self.reader_client.post(self.edit_url, self.form_data)
        assert response.status_code == HTTPStatus.NOT_FOUND
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, self.ORIGINAL_TITLE)
        self.assertEqual(note.text, self.ORIGINAL_TEXT)
        self.assertEqual(note.slug, self.ORIGINAL_SLUG)
        self.assertEqual(note.author, self.author)
