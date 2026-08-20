"""Тесты контента для проекта YaNews."""

import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count_on_home_page(client, home_url, multiple_news):
    """Проверка: на главной странице не более установленного числа новостей."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order_on_home_page(client, home_url, multiple_news):
    """Проверка: новости отсортированы от новых к старым."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order_on_detail_page(client, detail_url, multiple_comments):
    """Проверка: комментарии отсортированы от старых к новым."""
    response = client.get(detail_url)
    news_obj = response.context['news']
    all_comments = news_obj.comment_set.all()
    all_dates = [comment.created for comment in all_comments]
    assert all_dates == sorted(all_dates)


def test_anonymous_client_has_no_form(client, detail_url):
    """Проверка: анонимному пользователю недоступна форма комментариев."""
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, detail_url):
    """Проверка: авторизованному пользователю доступна форма комментариев."""
    response = author_client.get(detail_url)
    assert isinstance(response.context.get('form'), CommentForm)
