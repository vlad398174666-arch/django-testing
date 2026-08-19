"""Тесты маршрутов."""

from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', lf('news_id_for_args')),
        ('users:login', None),
        ('users:signup', None),
    ),
)
def test_pages_availability_for_anonymous_user(client, name, args):
    """Проверяет доступность общедоступных страниц для анонима."""
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_logout_availability_for_anonymous_user(client):
    """
    Проверяет доступность страницы выхода
    для анонима через POST-запрос.
    """
    url = reverse('users:logout')
    response = client.post(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, comment_id_for_args, expected_status
):
    """Проверяет доступ к редактированию и удалению чужих комментариев."""
    url = reverse(name, args=comment_id_for_args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirects(client, name, comment_id_for_args):
    """Проверяет редирект анонимного пользователя на страницу авторизации."""
    login_url = reverse('users:login')
    url = reverse(name, args=comment_id_for_args)
    expected_url = f'{login_url}?next={url}'

    response = client.get(url)
    assertRedirects(response, expected_url)
