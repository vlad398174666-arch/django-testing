"""Тестирование бизнес-логики приложения news."""

from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    """
    Проверяет, что анонимный пользователь
    не может создать комментарий.
    """
    url = reverse('news:detail', args=(news.id,))
    form_data = {'text': 'Текст комментария'}
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(author_client, author, news):
    """
    Проверяет, что авторизованный пользователь
    может создать комментарий.
    """
    url = reverse('news:detail', args=(news.id,))
    form_data = {'text': 'Текст комментария'}
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    """Проверяет блокировку комментариев со стоп-словами."""
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    form = response.context['form']
    assertFormError(form, field='text', errors=WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment, news):
    """Проверяет, что автор может удалить свой комментарий."""
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    delete_url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(not_author_client, comment):
    """Проверяет, что пользователь не может удалить чужой комментарий."""
    delete_url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment, news):
    """Проверяет, что автор может отредактировать свой комментарий."""
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    edit_url = reverse('news:edit', args=(comment.id,))
    form_data = {'text': 'Обновлённый комментарий'}
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
        not_author_client, comment, form_data=None
):
    """
    Проверяет, что пользователь
    не может отредактировать чужой комментарий.
    """
    edit_url = reverse('news:edit', args=(comment.id,))
    updated_data = {'text': 'Обновлённый комментарий'}
    response = not_author_client.post(edit_url, data=updated_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'
