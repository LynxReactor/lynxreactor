# agency/services/indexnow.py

import requests
import logging
import xml.etree.ElementTree as ET
from django.conf import settings

logger = logging.getLogger(__name__)


class IndexNowService:
    """
    Сервис для работы с IndexNow API
    Документация: https://www.indexnow.org/
    """

    def __init__(self):
        self.enabled = getattr(settings, 'INDEXNOW_ENABLED', False)
        self.key = getattr(settings, 'INDEXNOW_KEY', '')
        self.site_url = getattr(settings, 'SITE_URL', '')
        self.api_url = getattr(settings, 'INDEXNOW_API_URL', 'https://api.indexnow.org/IndexNow')

    def submit_urls(self, urls):
        """
        Отправка URL в IndexNow

        Args:
            urls: список URL или строка с одним URL

        Returns:
            bool: успешно ли отправлено
        """
        if not self.enabled:
            logger.info("IndexNow отключен в настройках")
            return False

        if not self.key:
            logger.warning("INDEXNOW_KEY не настроен")
            return False

        if not self.site_url:
            logger.warning("SITE_URL не настроен")
            return False

        # Преобразуем в список
        if isinstance(urls, str):
            urls = [urls]

        # Фильтруем и валидируем URL
        valid_urls = []
        for url in urls:
            if url.startswith(self.site_url) or url.startswith('/'):
                if url.startswith('/'):
                    url = f"{self.site_url}{url}"
                valid_urls.append(url)

        if not valid_urls:
            logger.warning("Нет валидных URL для отправки")
            return False

        # Формируем payload
        payload = {
            'host': self.site_url.replace('https://', '').replace('http://', ''),
            'key': self.key,
            'keyLocation': f"{self.site_url}/{self.key}.txt",
            'urlList': valid_urls
        }

        try:
            logger.info(f"Отправка в IndexNow: {len(valid_urls)} URL")

            response = requests.post(
                self.api_url,
                json=payload,
                timeout=10,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'LYNXREACTOR/1.0'
                }
            )

            if response.status_code == 200:
                logger.info(f"IndexNow успешно: {len(valid_urls)} URL")
                return True
            elif response.status_code == 202:
                logger.info(f"IndexNow принят (202): {len(valid_urls)} URL")
                return True
            elif response.status_code == 400:
                logger.error(f"IndexNow ошибка 400: {response.text}")
                return False
            elif response.status_code == 403:
                logger.error("IndexNow ошибка 403: Неверный ключ")
                return False
            elif response.status_code == 429:
                logger.error("IndexNow ошибка 429: Слишком много запросов")
                return False
            else:
                logger.error(f"IndexNow ошибка {response.status_code}: {response.text}")
                return False

        except requests.exceptions.Timeout:
            logger.error("IndexNow таймаут")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("IndexNow ошибка соединения")
            return False
        except Exception as e:
            logger.error(f"IndexNow ошибка: {str(e)}")
            return False

    def submit_single_url(self, url):
        """Отправка одного URL"""
        return self.submit_urls([url])

    def submit_blog_post(self, blog_post):
        """Отправка URL поста блога"""
        url = blog_post.get_absolute_url()
        return self.submit_urls([url])

    def submit_portfolio_item(self, portfolio_item):
        """Отправка URL проекта портфолио"""
        url = portfolio_item.get_absolute_url()
        return self.submit_urls([url])

    def submit_all_sitemap(self):
        """
        Отправка всех URL из sitemap
        Получает sitemap.xml через HTTP запрос с правильными заголовками
        """
        try:
            import requests
            import xml.etree.ElementTree as ET

            # Формируем URL для sitemap
            sitemap_url = f"{self.site_url}/sitemap.xml"

            # Правильные заголовки для запроса
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; LYNXREACTOR/1.0; +{})'.format(self.site_url),
                'Accept': 'application/xml, text/xml, */*',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            }

            logger.info(f"Запрос sitemap: {sitemap_url}")

            response = requests.get(
                sitemap_url,
                headers=headers,
                timeout=10,
                allow_redirects=True
            )

            if response.status_code != 200:
                logger.error(f"Не удалось получить sitemap: {response.status_code}")
                logger.error(f"Response: {response.text[:200]}")
                return False

            # Парсим XML
            try:
                root = ET.fromstring(response.content)
            except ET.ParseError as e:
                logger.error(f"Ошибка парсинга XML: {e}")
                logger.error(f"Content preview: {response.text[:200]}")
                return False

            urls = []
            # Пробуем с пространством имён
            namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            for loc in root.findall('.//sitemap:loc', namespace):
                url = loc.text
                if url and url.startswith(self.site_url):
                    urls.append(url)

            # Если не нашли с пространством имён, пробуем без него
            if not urls:
                for loc in root.findall('.//loc'):
                    url = loc.text
                    if url and url.startswith(self.site_url):
                        urls.append(url)

            # Если всё ещё нет URL, пробуем найти вложенные sitemap
            if not urls:
                # Проверяем, может быть это sitemap index
                for sitemap in root.findall('.//sitemap:sitemap', namespace):
                    loc = sitemap.find('sitemap:loc', namespace)
                    if loc is not None and loc.text:
                        # Рекурсивно обрабатываем вложенные sitemap
                        nested_urls = self._fetch_nested_sitemap(loc.text)
                        urls.extend(nested_urls)

            logger.info(f"Найдено {len(urls)} URL в sitemap")

            if not urls:
                logger.warning("Нет URL в sitemap для отправки")
                return False

            # Отправляем пакетами по 1000 URL (ограничение IndexNow)
            batch_size = 1000
            success = True
            for i in range(0, len(urls), batch_size):
                batch = urls[i:i + batch_size]
                if not self.submit_urls(batch):
                    success = False

            return success

        except requests.exceptions.Timeout:
            logger.error("Таймаут при запросе sitemap")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("Ошибка соединения при запросе sitemap")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка HTTP запроса к sitemap: {e}")
            return False
        except Exception as e:
            logger.error(f"Ошибка при отправке sitemap в IndexNow: {e}")
            return False

    def _fetch_nested_sitemap(self, url):
        """
        Рекурсивная загрузка вложенных sitemap
        """
        try:
            import requests
            import xml.etree.ElementTree as ET

            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; LYNXREACTOR/1.0; +{})'.format(self.site_url),
                'Accept': 'application/xml, text/xml, */*',
            }

            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return []

            root = ET.fromstring(response.content)
            urls = []
            namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

            for loc in root.findall('.//sitemap:loc', namespace):
                url_text = loc.text
                if url_text and url_text.startswith(self.site_url):
                    urls.append(url_text)

            if not urls:
                for loc in root.findall('.//loc'):
                    url_text = loc.text
                    if url_text and url_text.startswith(self.site_url):
                        urls.append(url_text)

            return urls

        except Exception as e:
            logger.error(f"Ошибка загрузки вложенного sitemap {url}: {e}")
            return []


# ============================================================
# СИНГЛТОН ДЛЯ ИСПОЛЬЗОВАНИЯ
# ============================================================

indexnow_service = IndexNowService()


# ============================================================
# УПРОЩЁННАЯ ФУНКЦИЯ ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ
# ============================================================

def send_to_indexnow(urls):
    """
    Упрощенная функция для отправки URL в IndexNow
    (для обратной совместимости)
    """
    return indexnow_service.submit_urls(urls)