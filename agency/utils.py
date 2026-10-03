# agency/utils.py

import hashlib
import ipaddress
import logging

from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


# ============================================================
# ДОВЕРЕННЫЕ ПРОКСИ
# ============================================================

def _get_trusted_proxies():
    """
    Список доверенных IP/сетей прокси из settings.TRUSTED_PROXIES.

    Формат: список строк, каждая — IP или CIDR.
    Пример: ['127.0.0.1', '::1', '10.0.0.0/8', '172.16.0.0/12']
    """
    from django.conf import settings
    return getattr(settings, 'TRUSTED_PROXIES', ['127.0.0.1', '::1'])


def _is_trusted_proxy(ip):
    """Проверка, что IP входит в список доверенных прокси (поддерживает CIDR)."""
    if not ip:
        return False
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False

    for trusted in _get_trusted_proxies():
        trusted = (trusted or '').strip()
        if not trusted:
            continue
        try:
            if '/' in trusted:
                if addr in ipaddress.ip_network(trusted, strict=False):
                    return True
            else:
                if addr == ipaddress.ip_address(trusted):
                    return True
        except ValueError:
            continue
    return False


# ============================================================
# IP КЛИЕНТА
# ============================================================

def get_client_ip(request) -> str:
    """
    Получить IP клиента.

    Порядок приоритета:
      1. HTTP_CF_CONNECTING_IP — если за Cloudflare
      2. HTTP_X_REAL_IP — Nginx (сам ставит $remote_addr)
      3. HTTP_X_FORWARDED_FOR — последний недоверенный (справа налево)
      4. REMOTE_ADDR — fallback
    """
    # 1. Cloudflare
    cf_ip = (request.META.get('HTTP_CF_CONNECTING_IP') or '').strip()
    if cf_ip:
        return cf_ip

    # 2. X-Real-IP — Nginx
    x_real_ip = (request.META.get('HTTP_X_REAL_IP') or '').strip()
    if x_real_ip:
        return x_real_ip

    # 3. X-Forwarded-For
    xff = (request.META.get('HTTP_X_FORWARDED_FOR') or '').strip()
    if xff:
        ips = [ip.strip() for ip in xff.split(',') if ip.strip()]
        # Справа налево — ищем первый недоверенный
        for ip in reversed(ips):
            if not _is_trusted_proxy(ip):
                return ip
        if ips:
            return ips[0]

    # 4. REMOTE_ADDR
    remote_addr = (request.META.get('REMOTE_ADDR') or '').strip()
    if remote_addr and remote_addr not in ('0.0.0.0', '::1', '127.0.0.1'):
        return remote_addr

    # 5. Fallback
    return '0.0.0.0'


# ============================================================
# RATE LIMIT
# ============================================================

def check_rate_limit(key: str, limit: int, period_seconds: int) -> tuple[bool, int]:
    """
    Простой rate limit с фиксированным окном.

    Хранит {'count': N, 'start': ts} в cache.

    Внимание: не атомарный — при одновременных запросах может
    пропустить на 1–2 запроса больше лимита. Для нашего случая
    (формы обратной связи) — приемлемо.
    """
    cache_key = f'ratelimit:{key}'
    now = int(timezone.now().timestamp())

    data = cache.get(cache_key)

    # Новое окно или истёкшее
    if data is None or not isinstance(data, dict) or (now - data.get('start', 0)) >= period_seconds:
        cache.set(
            cache_key,
            {'count': 1, 'start': now},
            period_seconds,
        )
        return True, limit - 1

    # В окне
    if data.get('count', 0) >= limit:
        return False, 0

    data['count'] = data.get('count', 0) + 1
    remaining_ttl = period_seconds - (now - data['start'])
    if remaining_ttl < 1:
        remaining_ttl = 1

    cache.set(cache_key, data, remaining_ttl)
    return True, limit - data['count']


# ============================================================
# RATE LIMIT KEY
# ============================================================

def get_rate_limit_key(prefix: str, request) -> str:
    """Ключ для rate limit: префикс + IP (хешированный)."""
    ip = get_client_ip(request)
    ip_hash = hashlib.md5(ip.encode()).hexdigest()[:16]
    return f'{prefix}:{ip_hash}'