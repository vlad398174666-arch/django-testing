"""Фикстуры для тестов."""

import pytest
from django.test.client import Client
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    """Создает и возвращает пользователя-автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Создает и возвращает обычного пользователя (не автора)."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Возвращает клиент, авторизованный от имени автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """
    Возвращает клиент,
    авторизованный от имени обычного пользователя.
    """
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Создает и возвращает объект новости."""
    return News.objects.create(title='Заголовок', text='Текст новости')


@pytest.fixture
def comment(news, author):
    """Создает и возвращает комментарий к новости."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
