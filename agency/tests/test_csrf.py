# agency/tests/test_csrf.py
"""
Тесты CSRF-защиты для AJAX endpoint'ов.

Django Test Client по умолчанию игнорирует CSRF. Чтобы проверить
реальную защиту — используем Client(enforce_csrf_checks=True).

Проверяем 3 endpoint'а:
- /api/contact/          — форма обратной связи
- /blog/vote/<id>/       — голосование за пост
- /api/subscribe/        — подписка на блог
"""
import json
import pytest
from django.test import Client
from django.urls import reverse


# ============================================================
# CONTACT
# ============================================================

@pytest.mark.django_db
class TestAjaxContactCSRF:
    """CSRF-защита /api/contact/."""

    @classmethod
    def setup_class(cls):
        cls.url = reverse('agency:ajax_contact')

    def _payload(self):
        return {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'This is a test message with enough characters.',
            'contact_method': 'email',
            'contact_value': 'john@example.com',
        }

    def test_post_without_csrf_returns_403(self):
        """POST без CSRF-токена → 403."""
        client = Client(enforce_csrf_checks=True)
        response = client.post(self.url, self._payload())
        assert response.status_code == 403

    def test_post_with_valid_csrf_passes(self):
        """POST с валидным CSRF → не 403."""
        client = Client(enforce_csrf_checks=True)

        # Первый GET устанавливает CSRF-cookie
        client.get(reverse('agency:home'))

        csrf_token = client.cookies['csrftoken'].value
        response = client.post(
            self.url,
            self._payload(),
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        # 200 (успех) или 400 (валидация) — но НЕ 403
        assert response.status_code != 403

    def test_post_with_invalid_csrf_returns_403(self):
        """POST с неправильным CSRF → 403."""
        client = Client(enforce_csrf_checks=True)
        client.get(reverse('agency:home'))

        response = client.post(
            self.url,
            self._payload(),
            HTTP_X_CSRFTOKEN='invalid-token-xyz',
        )
        assert response.status_code == 403


# ============================================================
# BLOG VOTE
# ============================================================

@pytest.mark.django_db
class TestBlogVoteCSRF:
    """CSRF-защита /blog/vote/<id>/."""

    def test_post_without_csrf_returns_403(self, blog_post):
        client = Client(enforce_csrf_checks=True)
        url = reverse('agency:blog_post_vote_by_id', kwargs={'post_id': blog_post.id})
        response = client.post(
            url,
            data=json.dumps({'vote_type': 'like'}),
            content_type='application/json',
        )
        assert response.status_code == 403

    def test_post_with_valid_csrf_passes(self, blog_post):
        client = Client(enforce_csrf_checks=True)
        client.get(reverse('agency:blog'))
        csrf_token = client.cookies['csrftoken'].value

        url = reverse('agency:blog_post_vote_by_id', kwargs={'post_id': blog_post.id})
        response = client.post(
            url,
            data=json.dumps({'vote_type': 'like'}),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        # 200 (голос принят) или 400 (валидация) — но не 403
        assert response.status_code != 403


# ============================================================
# SUBSCRIBE
# ============================================================

@pytest.mark.django_db
class TestAjaxSubscribeCSRF:
    """CSRF-защита /api/subscribe/."""

    def test_post_without_csrf_returns_403(self):
        client = Client(enforce_csrf_checks=True)
        url = reverse('agency:ajax_subscribe')
        response = client.post(url, {'email': 'test@example.com'})
        assert response.status_code == 403

    def test_post_with_valid_csrf_passes(self):
        client = Client(enforce_csrf_checks=True)
        client.get(reverse('agency:blog'))
        csrf_token = client.cookies['csrftoken'].value

        url = reverse('agency:ajax_subscribe')
        response = client.post(
            url,
            {'email': 'test@example.com'},
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        assert response.status_code != 403