# agency/error_handlers.py

from django.shortcuts import render
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


def _get_theme(request):
    """Тема из cookie (для страниц ошибок)."""
    try:
        return request.COOKIES.get('theme_preference', 'light')
    except AttributeError:
        return 'light'


def error_400(request, exception=None):
    """400 Bad Request"""
    logger.warning(f'400 Bad Request: {request.path}')
    return render(request, 'agency/errors/400.html', {
        'code': 400,
        'title': 'Некорректный запрос',
        'current_theme': _get_theme(request),
    }, status=400)


def error_403(request, exception=None):
    """403 Forbidden"""
    logger.warning(f'403 Forbidden: {request.path}')
    return render(request, 'agency/errors/403.html', {
        'code': 403,
        'title': 'Доступ запрещён',
        'current_theme': _get_theme(request),
    }, status=403)


def error_404(request, exception=None):
    """404 Not Found"""
    logger.warning(f'404 Not Found: {request.path}')
    return render(request, 'agency/errors/404.html', {
        'code': 404,
        'title': 'Страница не найдена',
        'current_theme': _get_theme(request),
    }, status=404)


def error_500(request):
    """500 Internal Server Error"""
    logger.error('500 Internal Server Error')
    return render(request, 'agency/errors/500.html', {
        'code': 500,
        'title': 'Внутренняя ошибка сервера',
        'current_theme': _get_theme(request),
    }, status=500)


def error_csrf_failure(request, reason=""):
    """CSRF Failure"""
    logger.warning(f'CSRF Failure: {reason}')
    return render(request, 'agency/errors/403.html', {
        'code': 403,
        'title': 'Ошибка безопасности',
        'reason': reason,
        'current_theme': _get_theme(request),
    }, status=403)


def error_404_json(request, exception=None):
    """404 для API (JSON)"""
    return JsonResponse({
        'error': 'Not Found',
        'message': 'The requested resource was not found.',
    }, status=404)