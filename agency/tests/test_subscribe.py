# agency/tests/test_subscribe.py

import pytest
from django.core.cache import cache
from django.urls import reverse

from agency.models import Subscriber


@pytest.fixture(autouse=True)
def clear_rate_limit():
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
class TestSubscribe:
    URL = None

    @classmethod
    def setup_class(cls):
        cls.URL = reverse('agency:ajax_subscribe')

    def test_get_method_not_allowed(self, client):
        response = client.get(self.URL)
        assert response.status_code == 405

    def test_valid_email_creates_subscriber(self, client):
        response = client.post(self.URL, {'email': 'new@example.com', 'source': 'test'})
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert Subscriber.objects.filter(email='new@example.com').exists()

    def test_duplicate_email_is_not_created(self, client, subscriber):
        response = client.post(self.URL, {'email': subscriber.email})
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert Subscriber.objects.filter(email=subscriber.email).count() == 1

    def test_email_lowercased(self, client):
        response = client.post(self.URL, {'email': 'New@Example.COM'})
        assert response.status_code == 200
        assert Subscriber.objects.filter(email='new@example.com').exists()

    def test_invalid_email_returns_400(self, client):
        response = client.post(self.URL, {'email': 'not-an-email'})
        assert response.status_code == 400
        assert response.json()['success'] is False

    def test_empty_email_returns_400(self, client):
        response = client.post(self.URL, {'email': ''})
        assert response.status_code == 400

    def test_resubscribe_reactivates(self, client, subscriber):
        subscriber.is_active = False
        subscriber.save(update_fields=['is_active'])
        response = client.post(self.URL, {'email': subscriber.email})
        assert response.status_code == 200
        subscriber.refresh_from_db()
        assert subscriber.is_active is True

    def test_rate_limit_blocks_after_3_requests(self, client):
        for i in range(3):
            response = client.post(self.URL, {'email': f'user{i}@example.com'})
            assert response.status_code == 200, f'Failed at attempt {i+1}'
        response = client.post(self.URL, {'email': 'user4@example.com'})
        assert response.status_code == 429


@pytest.mark.django_db
class TestUnsubscribe:
    def test_valid_token_unsubscribes(self, client, subscriber):
        url = reverse('agency:unsubscribe') + f'?token={subscriber.unsubscribe_token}'
        response = client.get(url)
        assert response.status_code == 200
        subscriber.refresh_from_db()
        assert subscriber.is_active is False
        assert subscriber.unsubscribed_at is not None

    def test_invalid_token_shows_error(self, client):
        url = reverse('agency:unsubscribe') + '?token=invalid'
        response = client.get(url)
        assert response.status_code == 200
        # Проверяем, что статус в контексте — 'invalid'
        assert response.context['status'] == 'invalid'

    def test_already_unsubscribed_shows_info(self, client, subscriber):
        subscriber.unsubscribe()
        url = reverse('agency:unsubscribe') + f'?token={subscriber.unsubscribe_token}'
        response = client.get(url)
        assert response.status_code == 200
        assert response.context['status'] == 'already_unsubscribed'

    def test_missing_token_shows_invalid(self, client):
        url = reverse('agency:unsubscribe')
        response = client.get(url)
        assert response.status_code == 200
        assert response.context['status'] == 'invalid'