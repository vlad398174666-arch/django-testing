"""Тестирование бизнес-логики приложения news."""

from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

FORM_DATA = {'text': 'Текст комментария'}
NEW_FORM_DATA = {'text': 'Обновлённый комментарий'}


def test_anonymous_user_cant_create_comment(client, detail_url):
    """
    Проверяет, что анонимный пользователь
    не может создать комментарий.
    """
    Comment.objects.all().delete()
    client.post(detail_url, data=FORM_DATA)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, news, detail_url):
    """
    Проверяет, что авторизованный пользователь
    может создать комментарий.
    """
    Comment.objects.all().delete()
    author_client.post(detail_url, data=FORM_DATA)
    assert Comment.objects.count() == 1

    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, detail_url, bad_word):
    """Проверяет блокировку комментариев со всеми стоп-словами."""
    Comment.objects.all().delete()
    bad_words_data = {'text': f'Какой-то текст, {bad_word}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(response.context['form'], field='text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, delete_url):
    """Проверяет, что автор может удалить свой комментарий."""
    comments_count_before = Comment.objects.count()
    author_client.delete(delete_url)
    assert Comment.objects.count() == comments_count_before - 1


def test_user_cant_delete_comment_of_another_user(
        not_author_client,
        delete_url,
):
    """Проверяет, что пользователь не может удалить чужую комментарий."""
    comments_count_before = Comment.objects.count()
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count_before


def test_author_can_edit_comment(author_client, edit_url, comment):
    """Проверяет, что автор может отредактировать свой комментарий."""
    comments_count_before = Comment.objects.count()
    author_client.post(edit_url, data=NEW_FORM_DATA)

    comment.refresh_from_db()
    assert comment.text == NEW_FORM_DATA['text']
    assert Comment.objects.count() == comments_count_before


def test_user_cant_edit_comment_of_another_user(
        not_author_client,
        edit_url,
        comment,
):
    """
    Проверяет, что пользователь
    не может отредактировать чужой комментарий.
    """
    comments_count_before = Comment.objects.count()
    original_text = comment.text
    response = not_author_client.post(edit_url, data=NEW_FORM_DATA)

    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == original_text
    assert Comment.objects.count() == comments_count_before
