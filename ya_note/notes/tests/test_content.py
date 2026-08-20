"""Тесты контента для проекта YaNote."""

from notes.forms import NoteForm
from notes.tests.base import BaseTest


class TestContent(BaseTest):
    """Класс для тестирования контента."""

    def test_note_in_list_for_author(self):
        """Заметка передаётся на страницу со списком в object_list."""
        self.client.force_login(self.author)
        response = self.client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_another_user(self):
        """В список заметок не попадают заметки другого пользователя."""
        self.client.force_login(self.reader)
        response = self.client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_pages_contain_form(self):
        """На страницы создания и редактирования передаются формы."""
        self.client.force_login(self.author)
        urls = (self.add_url, self.edit_url)
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIsInstance(response.context.get('form'), NoteForm)
