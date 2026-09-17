# agency/tests/test_admin_smoke.py
"""
Smoke-тесты админки.

Цель — поймать падения страниц ДО миграции Django 4.2 → 5.2
(Jazzmin, modeltranslation, ckeditor — основные подозреваемые).
"""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestAdminSmoke:
    """GET changelist каждой ключевой модели → 200."""

    def _admin_url(self, app_label, model_name):
        return reverse(f'admin:{app_label}_{model_name}_changelist')

    def test_blogpost_admin_loads(self, admin_client):
        response = admin_client.get(self._admin_url('agency', 'blogpost'))
        assert response.status_code == 200

    def test_contactrequest_admin_loads(self, admin_client):
        response = admin_client.get(self._admin_url('agency', 'contactrequest'))
        assert response.status_code == 200

    def test_tariff_admin_loads(self, admin_client):
        response = admin_client.get(self._admin_url('agency', 'tariff'))
        assert response.status_code == 200

    def test_contactpage_admin_loads(self, admin_client):
        response = admin_client.get(self._admin_url('agency', 'contactpage'))
        assert response.status_code == 200

    def test_siteconfiguration_admin_loads(self, admin_client):
        response = admin_client.get(
            self._admin_url('agency', 'siteconfiguration')
        )
        assert response.status_code == 200