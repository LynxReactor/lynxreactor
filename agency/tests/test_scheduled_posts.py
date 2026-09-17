# agency/tests/test_scheduled_posts.py
"""
Тесты запланированных статей (published_at в будущем).

Ключевая идея: будущая статья с is_published=True, is_active=True
НЕ должна появляться:
- в списке блога
- в детальной (404)
- в категории
- в related/next других статей
- в sitemap
- в vote endpoints (404)
- в popular_posts
- в newsletter
- в post_count категории
"""
from datetime import timedelta
from unittest.mock import patch
import pytest
from django.urls import reverse
from django.utils import timezone

from agency.models import BlogPost, Subscriber
from agency.tasks import send_blog_post_newsletter


# ============================================================
# ФИКСТУРЫ
# ============================================================

@pytest.fixture
def future_post(db, blog_category):
    """Будущая статья: published_at = +7 дней."""
    return BlogPost.objects.create(
        category=blog_category,
        title='Future Scheduled Post',
        slug='future-scheduled-post',
        excerpt='Future excerpt',
        content='<p>Future content</p>',
        author='LYNXREACTOR',
        is_published=True,
        is_active=True,
        published_at=timezone.now() + timedelta(days=7),
    )


# ============================================================
# BLOG LIST
# ============================================================

@pytest.mark.django_db
class TestFuturePostInBlogList:

    def test_future_post_not_in_blog_list(self, client, future_post):
        response = client.get(reverse('agency:blog'))
        assert future_post.title.encode() not in response.content
        posts = list(response.context['posts'])
        assert future_post not in posts

    def test_future_post_not_in_popular_posts(self, client, future_post):
        """Будущий пост не попадает в popular_posts (сайдбар)."""
        response = client.get(reverse('agency:blog'))
        popular = list(response.context['popular_posts'])
        assert future_post not in popular

    def test_future_post_not_counted_in_category(self, client, blog_post, future_post, blog_category):
        """post_count категории не учитывает будущую статью.

        В БД есть 2 поста в категории:
        - blog_post: published_at = now        → считается
        - future_post: published_at = now + 7  → НЕ считается
        Ожидаем post_count = 1.
        """
        response = client.get(reverse('agency:blog'))
        categories = list(response.context['categories'])
        cat = next(c for c in categories if c.id == blog_category.id)
        assert cat.post_count == 1


# ============================================================
# BLOG DETAIL
# ============================================================

@pytest.mark.django_db
class TestFuturePostDetail:

    def test_future_post_detail_404(self, client, future_post):
        url = reverse('agency:blog_detail', kwargs={'slug': future_post.slug})
        response = client.get(url)
        assert response.status_code == 404


# ============================================================
# BLOG CATEGORY
# ============================================================

@pytest.mark.django_db
class TestFuturePostInCategory:

    def test_future_post_not_in_category_list(self, client, future_post):
        url = reverse('agency:blog_category', kwargs={'slug': future_post.category.slug})
        response = client.get(url)
        assert future_post.title.encode() not in response.content
        posts = list(response.context['posts'])
        assert future_post not in posts


# ============================================================
# RELATED / NEXT
# ============================================================

@pytest.mark.django_db
class TestFuturePostInRelatedAndNext:

    def test_future_post_not_in_related(self, client, blog_post, future_post):
        """Будущий пост не появляется в related_posts."""
        url = reverse('agency:blog_detail', kwargs={'slug': blog_post.slug})
        response = client.get(url)
        related = list(response.context['related_posts'])
        assert future_post not in related

    def test_future_post_not_in_next(self, client, blog_post, future_post):
        """Будущий пост не появляется в next_post."""
        url = reverse('agency:blog_detail', kwargs={'slug': blog_post.slug})
        response = client.get(url)
        assert response.context['next_post'] != future_post


# ============================================================
# SITEMAP
# ============================================================

@pytest.mark.django_db
class TestFuturePostInSitemap:

    def test_future_post_not_in_sitemap(self, client, future_post):
        response = client.get('/sitemap.xml')
        assert response.status_code == 200
        assert future_post.slug.encode() not in response.content


# ============================================================
# VOTE
# ============================================================

@pytest.mark.django_db
class TestFuturePostVote:

    def test_vote_by_slug_404(self, client, future_post):
        url = reverse('agency:blog_post_vote', kwargs={'slug': future_post.slug})
        response = client.post(
            url,
            data='{"vote_type":"like"}',
            content_type='application/json',
        )
        assert response.status_code == 404

    def test_vote_by_id_404(self, client, future_post):
        url = reverse('agency:blog_post_vote_by_id', kwargs={'post_id': future_post.id})
        response = client.post(
            url,
            data='{"vote_type":"like"}',
            content_type='application/json',
        )
        assert response.status_code == 404


# ============================================================
# NEWSLETTER
# ============================================================

@pytest.mark.django_db
class TestFuturePostNewsletter:

    def test_newsletter_skips_future_post(self, future_post, subscriber):
        """Рассылка не отправляется для будущего поста."""
        result = send_blog_post_newsletter(future_post.id)
        assert 'not found' in result.lower()