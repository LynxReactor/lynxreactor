# agency/tests/test_turnstile.py
"""
Тесты Cloudflare Turnstile-проверки в ajax_contact.

Реальный Cloudflare НЕ вызываем — мокаем requests.post.

ВАЖНО: conftest.py (autouse) ставит TURNSTILE_DISABLED=True.
Здесь через фикстуру turnstile_enabled включаем проверку.
"""
from unittest.mock import patch, Mock
import pytest
import requests
from django.urls import reverse

from agency.models import ContactRequest


# ============================================================
# ФИКСТУРЫ
# ============================================================

@pytest.fixture
def turnstile_enabled(settings):
    """Включает Turnstile-проверку в ajax_contact."""
    settings.DEBUG = False
    settings.TURNSTILE_DISABLED = False
    settings.CF_TURNSTILE_SECRET_KEY = 'test-secret-key'
    settings.CF_TURNSTILE_VERIFY_URL = (
        'https://challenges.cloudflare.com/turnstile/v0/siteverify'
    )
    yield


@pytest.fixture
def payload():
    """Валидные данные формы."""
    return {
        'name': 'John Doe',
        'email': 'john@example.com',
        'message': 'This is a test message with enough characters.',
        'contact_method': 'email',
        'contact_value': 'john@example.com',
        'cf-turnstile-response': 'dummy-token',
    }


def _mock_response(json_data, status_code=200):
    """Хелпер: создаёт Mock с json() и status_code."""
    mock = Mock()
    mock.status_code = status_code
    mock.json.return_value = json_data
    return mock


# ============================================================
# ТЕСТЫ
# ============================================================

@pytest.mark.django_db
class TestTurnstile:
    URL = None

    @classmethod
    def setup_class(cls):
        cls.URL = reverse('agency:ajax_contact')

    # ----- 1. УСПЕХ -----

    @patch('agency.views.requests.post')
    def test_success_creates_contact(self, mock_post, client, payload, turnstile_enabled):
        """Cloudflare вернул success=true → заявка создана."""
        mock_post.return_value = _mock_response({'success': True})

        response = client.post(self.URL, payload)

        assert response.status_code == 200
        assert response.json()['success'] is True
        assert ContactRequest.objects.count() == 1

    # ----- 2. FAILURE -----

    @patch('agency.views.requests.post')
    def test_failure_returns_400(self, mock_post, client, payload, turnstile_enabled):
        """Cloudflare вернул success=false → 400, заявка не создана."""
        mock_post.return_value = _mock_response({
            'success': False,
            'error-codes': ['invalid-input-response'],
        })

        response = client.post(self.URL, payload)

        assert response.status_code == 400
        assert response.json()['success'] is False
        assert 'error' in response.json()
        assert ContactRequest.objects.count() == 0

    @patch('agency.views.requests.post')
    def test_timeout_error_code(self, mock_post, client, payload, turnstile_enabled):
        """Cloudflare вернул error-codes=['timeout'] → 400, заявка не создана."""
        mock_post.return_value = _mock_response({
            'success': False,
            'error-codes': ['timeout'],
        })

        response = client.post(self.URL, payload)

        assert response.status_code == 400
        assert response.json()['success'] is False
        assert ContactRequest.objects.count() == 0

    @patch('agency.views.requests.post')
    def test_invalid_secret_key_returns_400(self, mock_post, client, payload, turnstile_enabled):
        """Cloudflare вернул invalid-input-secret → 400, заявка не создана."""
        mock_post.return_value = _mock_response({
            'success': False,
            'error-codes': ['invalid-input-secret'],
        })

        response = client.post(self.URL, payload)

        assert response.status_code == 400
        assert response.json()['success'] is False
        assert ContactRequest.objects.count() == 0

    # ----- 3. HTTP TIMEOUT -----

    @patch('agency.views.requests.post')
    def test_http_timeout_returns_503(self, mock_post, client, payload, turnstile_enabled):
        """requests.post выбросил Timeout → 503."""
        mock_post.side_effect = requests.exceptions.Timeout()

        response = client.post(self.URL, payload)

        assert response.status_code == 503
        assert response.json()['success'] is False
        assert ContactRequest.objects.count() == 0

    # ----- 4. CONNECTION ERROR -----

    @patch('agency.views.requests.post')
    def test_connection_error_returns_503(self, mock_post, client, payload, turnstile_enabled):
        """requests.post выбросил ConnectionError → 503."""
        mock_post.side_effect = requests.exceptions.ConnectionError()

        response = client.post(self.URL, payload)

        assert response.status_code == 503
        assert response.json()['success'] is False
        assert ContactRequest.objects.count() == 0

    # ----- 5. НЕТ TOKEN -----

    @patch('agency.views.requests.post')
    def test_missing_token_returns_400(self, mock_post, client, turnstile_enabled):
        """Нет cf-turnstile-response → 400, Cloudflare НЕ вызывается."""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'This is a test message with enough characters.',
            'contact_method': 'email',
            'contact_value': 'john@example.com',
            # cf-turnstile-response отсутствует
        }

        response = client.post(self.URL, data)

        assert response.status_code == 400
        assert response.json()['success'] is False
        # requests.post НЕ вызывался — Cloudflare не трогаем без token
        mock_post.assert_not_called()
        assert ContactRequest.objects.count() == 0

    # ----- 6. DISABLED (DEBUG=True) -----

    @patch('agency.views.requests.post')
    def test_disabled_in_debug_mode(self, mock_post, client, payload, settings):
        """В DEBUG=True Turnstile не проверяется."""
        settings.DEBUG = True
        settings.TURNSTILE_DISABLED = True

        response = client.post(self.URL, payload)

        assert response.status_code == 200
        assert ContactRequest.objects.count() == 1
        # requests.post НЕ вызывался
        mock_post.assert_not_called()