# agency/tests/test_views.py

import pytest
from django.urls import reverse


# ============================================================
# ГЛАВНАЯ
# ============================================================

@pytest.mark.django_db
class TestIndexView:
    def test_home_returns_200(self, client):
        response = client.get(reverse('agency:home'))
        assert response.status_code == 200

    def test_home_uses_correct_template(self, client):
        response = client.get(reverse('agency:home'))
        assert 'agency/home.html' in [t.name for t in response.templates]

    def test_home_contains_seo_title(self, client):
        response = client.get(reverse('agency:home'))
        assert b'<title>' in response.content


# ============================================================
# КОНТАКТЫ
# ============================================================

@pytest.mark.django_db
class TestContactView:
    def test_contact_returns_200(self, client):
        response = client.get(reverse('agency:contact'))
        assert response.status_code == 200

    def test_contact_uses_correct_template(self, client):
        response = client.get(reverse('agency:contact'))
        assert 'agency/contact.html' in [t.name for t in response.templates]

    def test_contact_shows_hero_cta_buttons(self, client, hero_contacts):
        response = client.get(reverse('agency:contact'))
        content = response.content.decode('utf-8')
        assert 'На главную' in content or 'href="/"' in content


# ============================================================
# БЛОГ
# ============================================================

@pytest.mark.django_db
class TestBlogListView:
    def test_blog_returns_200(self, client):
        response = client.get(reverse('agency:blog'))
        assert response.status_code == 200

    def test_blog_uses_correct_template(self, client):
        response = client.get(reverse('agency:blog'))
        assert 'agency/blog_list.html' in [t.name for t in response.templates]

    def test_blog_shows_published_posts(self, client, blog_post):
        response = client.get(reverse('agency:blog'))
        assert blog_post.title.encode() in response.content

    def test_blog_hides_draft_posts(self, client, draft_post):
        response = client.get(reverse('agency:blog'))
        assert draft_post.title.encode() not in response.content

    def test_blog_search_filters_posts(self, client, blog_post):
        response = client.get(reverse('agency:blog') + '?q=Test')
        assert blog_post.title.encode() in response.content

    def test_blog_search_no_match(self, client, blog_post):
        response = client.get(reverse('agency:blog') + '?q=nonexistent_xyz')
        assert response.status_code == 200
        # Проверяем контекст, а не HTML целиком — «Популярные статьи» в сайдбаре
        # выводятся без учёта поиска (by design), поэтому в HTML title есть всегда.
        posts = list(response.context['posts'])
        assert len(posts) == 0


@pytest.mark.django_db
class TestBlogDetailView:
    def test_detail_returns_200(self, client, blog_post):
        url = reverse('agency:blog_detail', kwargs={'slug': blog_post.slug})
        response = client.get(url)
        assert response.status_code == 200

    def test_detail_uses_correct_template(self, client, blog_post):
        url = reverse('agency:blog_detail', kwargs={'slug': blog_post.slug})
        response = client.get(url)
        assert 'agency/blog_detail.html' in [t.name for t in response.templates]

    def test_detail_404_for_nonexistent_slug(self, client):
        url = reverse('agency:blog_detail', kwargs={'slug': 'nonexistent'})
        response = client.get(url)
        assert response.status_code == 404

    def test_detail_404_for_draft(self, client, draft_post):
        url = reverse('agency:blog_detail', kwargs={'slug': draft_post.slug})
        response = client.get(url)
        assert response.status_code == 404

    def test_detail_increments_views(self, client, blog_post):
        initial_views = blog_post.views
        url = reverse('agency:blog_detail', kwargs={'slug': blog_post.slug})
        client.get(url)
        blog_post.refresh_from_db()
        assert blog_post.views == initial_views + 1


@pytest.mark.django_db
class TestBlogCategoryView:
    def test_category_returns_200(self, client, blog_post):
        url = reverse('agency:blog_category', kwargs={'slug': blog_post.category.slug})
        response = client.get(url)
        assert response.status_code == 200

    def test_category_404_for_invalid_slug(self, client):
        url = reverse('agency:blog_category', kwargs={'slug': 'nonexistent'})
        response = client.get(url)
        assert response.status_code == 404