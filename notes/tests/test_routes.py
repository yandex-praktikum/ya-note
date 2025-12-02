from http import HTTPStatus

from .notes_base import NotesBaseTestCase

OK = HTTPStatus.OK
NOT_FOUND = HTTPStatus.NOT_FOUND


class TestRoutes(NotesBaseTestCase):

    def test_page_availability(self):
        cases = (
            (self.home_url, self.anonymous_client, 'get', OK),
            (self.login_url, self.anonymous_client, 'get', OK),
            (self.signup_url, self.anonymous_client, 'get', OK),
            (self.logout_url, self.anonymous_client, 'post', OK),
            (self.list_url, self.author_client, 'get', OK),
            (self.add_url, self.author_client, 'get', OK),
            (self.success_url, self.author_client, 'get', OK),
            (self.detail_url, self.author_client, 'get', OK),
            (self.edit_url, self.author_client, 'get', OK),
            (self.delete_url, self.author_client, 'get', OK),
            (self.detail_url, self.reader_client, 'get', NOT_FOUND),
            (self.edit_url, self.reader_client, 'get', NOT_FOUND),
            (self.delete_url, self.reader_client, 'get', NOT_FOUND),
        )

        for url, client, method, expected in cases:
            with self.subTest(url=url, method=method):
                if method == 'get':
                    response = client.get(url)
                else:
                    response = client.post(url)
                self.assertEqual(response.status_code, expected)

    def test_redirect_for_anonymous_client(self):
        urls = (
            (self.success_url, None),
            (self.add_url, None),
            (self.detail_url, self.note.slug),
            (self.edit_url, self.note.slug),
            (self.delete_url, self.note.slug),
        )
        for url, slug in urls:
            with self.subTest(name=url):
                response = self.client.get(url)
                redirect_url = f'{self.login_url}?next={url}'
                self.assertRedirects(response, redirect_url)
