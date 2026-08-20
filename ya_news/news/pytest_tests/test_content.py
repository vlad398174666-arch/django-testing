"""Тесты контента для проекта YaNews."""

from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.forms import CommentForm
from news.models import Comment, News

pytestmark = pytest.mark.django_db

HOME_URL = reverse('news:home')


@pytest.fixture
def multiple_news():
    """Создает 11 новостей для проверки пагинации и сортировки."""
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def multiple_comments(news, author):
    """Создает два комментария к новости с разным временем."""
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Текст {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()


def test_news_count_on_home_page(client, multiple_news):
    """Проверка: на главной странице не более 10 новостей."""
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order_on_home_page(client, multiple_news):
    """Проверка: новости отсортированы от новых к старым."""
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order_on_detail_page(client, news, multiple_comments):
    """Проверка: комментарии отсортированы от старых к новым."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    news_obj = response.context['news']
    all_comments = news_obj.comment_set.all()
    all_dates = [comment.created for comment in all_comments]
    assert all_dates == sorted(all_dates)


def test_anonymous_client_has_no_form(client, news):
    """Проверка: анонимному пользователю недоступна форма комментариев."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news):
    """Проверка: авторизованному пользователю доступна форма комментариев."""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
