"""Тесты маршрутов для проекта YaNews."""

from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf

pytestmark = pytest.mark.django_db

PUBLIC_URLS = (
    lf('home_url'),
    lf('detail_url'),
    lf('login_url'),
    lf('signup_url'),
)

EDIT_DELETE_URLS = (
    lf('edit_url'),
    lf('delete_url'),
)


@pytest.mark.parametrize('url', PUBLIC_URLS)
def test_pages_availability_for_anonymous_user(client, url):
    """
    Проверяет доступность общедоступных страниц
    для анонима (GET-запросы).
    """
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_logout_availability_for_anonymous_user(client, logout_url):
    """Проверяет доступность страницы выхода для анонима (POST-запрос)."""
    response = client.post(logout_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize('url', EDIT_DELETE_URLS)
def test_pages_availability_for_different_users(
        parametrized_client, url, expected_status
):
    """Проверяет доступ к редактированию и удалению чужих комментариев."""
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('url', EDIT_DELETE_URLS)
def test_redirects(client, url, login_url):
    """Проверяет редирект анонимного пользователя на авторизацию."""
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


def test_successful_creation_redirects(author_client, detail_url):
    """Проверяет редирект после успешного создания комментария."""
    url_to_comments = detail_url + '#comments'
    response = author_client.post(
        detail_url, data={'text': 'Текст комментария'}
    )
    assertRedirects(response, url_to_comments)


def test_successful_edit_redirects(author_client, edit_url, detail_url):
    """Проверяет редирект после успешного редактирования."""
    url_to_comments = detail_url + '#comments'
    response = author_client.post(
        edit_url, data={'text': 'Обновлённый комментарий'}
    )
    assertRedirects(response, url_to_comments)


def test_successful_delete_redirects(author_client, delete_url, detail_url):
    """Проверяет редирект после успешного удаления."""
    url_to_comments = detail_url + '#comments'
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
