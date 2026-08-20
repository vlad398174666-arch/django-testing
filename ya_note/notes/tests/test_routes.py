"""Тесты маршрутов для проекта YaNote."""

from http import HTTPStatus

from notes.tests.base import BaseTest


class TestRoutes(BaseTest):
    """Класс для проверки маршрутов."""

    def test_pages_availability_for_anonymous_user(self):
        """Проверка доступности страниц для анонимного пользователя."""
        urls = (self.home_url, self.login_url, self.signup_url)
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_availability_for_anonymous_user(self):
        """Проверка доступности страницы выхода для анонима (POST-запрос)."""
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Проверка доступности страниц для авторизованного пользователя."""
        urls = (self.list_url, self.success_url, self.add_url)
        self.client.force_login(self.author)
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        """Проверка прав доступа к редактированию и удалению заметки."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = (self.detail_url, self.edit_url, self.delete_url)
        for user, status in users_statuses:
            self.client.force_login(user)
            for url in urls:
                with self.subTest(user=user, url=url):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверка редиректов для анонимного пользователя."""
        urls = (
            self.list_url, self.success_url, self.add_url,
            self.detail_url, self.edit_url, self.delete_url
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_redirect_after_note_creation(self):
        """Проверка редиректа после создания заметки."""
        self.client.force_login(self.author)
        response = self.client.post(
            self.add_url,
            data={'title': '1', 'text': '1', 'slug': '1'}
        )
        self.assertRedirects(response, self.success_url)

    def test_redirect_after_note_edit(self):
        """Проверка редиректа после редактирования заметки."""
        self.client.force_login(self.author)
        response = self.client.post(
            self.edit_url,
            data={'title': '1', 'text': '1', 'slug': '1'}
        )
        self.assertRedirects(response, self.success_url)

    def test_redirect_after_note_delete(self):
        """Проверка редиректа после удаления заметки."""
        self.client.force_login(self.author)
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, self.success_url)
