from http import HTTPStatus

from notes.forms import NoteForm
from notes.tests.notes_base import NotesBaseTestCase


class TestContent(NotesBaseTestCase):

    def test_list_note_availability(self):
        data = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        for client, expected in data:
            with self.subTest(client=client):
                response = client.get(self.list_url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                object_list = response.context['object_list']
                if expected:
                    self.assertIn(self.note, object_list)
                else:
                    self.assertNotIn(self.note, object_list)

    def test_authorized_client_has_form(self):
        urls = (
            (self.edit_url),
            (self.add_url),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
