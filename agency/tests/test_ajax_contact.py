# agency/tests/test_ajax_contact.py

import json
import pytest
from django.core.cache import cache
from django.urls import reverse

from agency.models import ContactRequest, Tariff


@pytest.fixture(autouse=True)
def clear_rate_limit():
    """Чистим rate limit перед каждым тестом."""
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
class TestAjaxContact:
    URL = None

    @classmethod
    def setup_class(cls):
        cls.URL = reverse('agency:ajax_contact')

    def _payload(self, **overrides):
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'This is a test message with enough characters.',
            'contact_method': 'email',
            'contact_value': 'john@example.com',
            'cf-turnstile-response': 'dummy-token',
        }
        data.update(overrides)
        return data

    def test_get_method_not_allowed(self, client):
        response = client.get(self.URL)
        assert response.status_code == 405

    def test_valid_submission_creates_contact(self, client, settings):
        response = client.post(self.URL, self._payload())
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert ContactRequest.objects.count() == 1
        assert ContactRequest.objects.first().email == 'john@example.com'

    def test_missing_name_returns_errors(self, client, settings):
        response = client.post(self.URL, self._payload(name=''))
        assert response.status_code == 400
        data = response.json()
        assert data['success'] is False
        assert 'name' in data['errors']

    def test_short_name_returns_errors(self, client, settings):
        response = client.post(self.URL, self._payload(name='J'))
        assert response.status_code == 400
        assert 'name' in response.json()['errors']

    def test_invalid_email_returns_errors(self, client, settings):
        response = client.post(self.URL, self._payload(email='not-an-email'))
        assert response.status_code == 400
        assert 'email' in response.json()['errors']

    def test_short_message_returns_errors(self, client, settings):
        response = client.post(self.URL, self._payload(message='short'))
        assert response.status_code == 400
        assert 'message' in response.json()['errors']

    def test_missing_contact_method_returns_errors(self, client, settings):
        response = client.post(self.URL, self._payload(contact_method=''))
        assert response.status_code == 400
        assert 'contact_method' in response.json()['errors']

    def test_valid_tariff_is_attached(self, client, settings, tariff):
        response = client.post(self.URL, self._payload(tariff=str(tariff.id)))
        assert response.status_code == 200
        contact = ContactRequest.objects.first()
        assert contact.tariff == tariff

    def test_rate_limit_blocks_after_5_requests(self, client, settings):
        for i in range(5):
            response = client.post(self.URL, self._payload(email=f'user{i}@example.com'))
            assert response.status_code == 200, f'Failed at attempt {i+1}'
        # 6-й — должен быть заблокирован
        response = client.post(self.URL, self._payload(email='user6@example.com'))
        assert response.status_code == 429

    def test_invalid_json_returns_400(self, client, settings):
        response = client.post(
            self.URL,
            data='not json',
            content_type='application/json',
        )
        assert response.status_code == 400