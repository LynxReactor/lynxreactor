# LYNXREACTOR

> **The Engine of Web Evolution** — премиальная веб-студия на Python/Django.

Корпоративный сайт [lynxreactor.by](https://lynxreactor.by) — портфолио, блог, тарифы, отзывы и формы обратной связи. Полностью двуязычный (RU / EN), с поддержкой светлой и тёмной темы.

---

## 🚀 Стек

| Компонент | Технология |
|-----------|-----------|
| **Backend** | Python 3.12, Django 4.2.30 |
| **Database** | PostgreSQL (prod) / SQLite (dev) |
| **Cache / Broker** | Redis |
| **Task Queue** | Celery + Celery Beat |
| **Admin UI** | django-jazzmin |
| **i18n** | django-modeltranslation |
| **WYSIWYG** | django-ckeditor |
| **Images** | django-imagekit |
| **Captcha** | Cloudflare Turnstile |
| **Frontend** | Vanilla JS, CSS variables |

---

## ✨ Возможности

### Публичный сайт
- 🎨 Две темы (light / dark) с сохранением в localStorage + cookie
- 🌍 Двуязычный интерфейс (RU / EN) — Django i18n + modeltranslation
- 🖼️ Themed images — 4 варианта (theme × language) для каждой секции
- 📰 Блог — категории, голосование (like / dislike), подписка на рассылку, PDF
- 📊 Портфолио — теги технологий, ссылки на проекты
- 💰 Тарифы — переключение валют (BYN / RUB / EUR / USD)
- 📧 Формы обратной связи — Turnstile, rate limit, email + Telegram
- 📱 Адаптивная вёрстка — mobile-first

### Админка (Jazzmin)
- 🎛️ Управление всеми секциями без кода
- 🌐 Встроенный переводчик (RU / EN) для каждой модели
- 📦 JSON-редактор для сложных полей (features, technologies, tags)
- 🖼️ Превью изображений прямо в списках
- 📤 Массовый экспорт в CSV / JSON
- 📋 Дублирование записей
- 📨 Массовые email-рассылки подписчикам
- 📱 Telegram-уведомления о новых заявках

### SEO
- 🌐 SEO-настройки для каждой страницы (RU / EN, OG, keywords)
- 📄 Sitemap.xml + robots.txt
- 🏷️ Structured Data (JSON-LD) — WebSite, Organization, BlogPosting
- 🔗 Canonical URLs
- 📮 IndexNow — интеграция с Bing / Yandex

### Надёжность
- ⚡ Celery retry с backoff для временных ошибок email; ошибки Telegram не блокируют уведомление
- 🔒 CSRF-защита (тесты с enforce_csrf_checks=True)
- 🛡️ Rate limiting — 5 заявок/час, 3 подписки/час, 20 голосов/час
- 🗓️ Отложенная публикация — published_at в будущем
- 💾 transaction.on_commit для сигналов
- 📝 PDF-валидация — extension + %PDF- signature

---

## 📦 Установка

### Требования
- Python 3.11+
- Redis (опционально — для Celery в dev)
- PostgreSQL (для production)
- gettext (для компиляции переводов)

### Быстрый старт (dev)

```bash
# 1. Клонировать
git clone https://github.com/LynxReactor/lynxreactor.git
cd lynxreactor

# 2. Виртуальное окружение
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Зависимости
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Окружение
cp .env.example .env
# Отредактировать .env — SECRET_KEY, EMAIL и т.д.

# 5. БД
python manage.py migrate

# 6. Суперпользователь
python manage.py createsuperuser

# 7. Переводы
python manage.py compilemessages

# 8. Запуск
python manage.py runserver
```

**Открыть:**
- Сайт: http://127.0.0.1:8000/
- Админка: http://127.0.0.1:8000/admin/

### Альтернатива — `manage_project.py`

```bash
python manage_project.py setup       # полная настройка
python manage_project.py dev         # запуск dev
python manage_project.py test        # тесты
python manage_project.py check_i18n  # аудит переводов
```

Полный список: `python manage_project.py --help`.

---

## 🧪 Тесты

```bash
python manage_project.py test          # все тесты
python manage_project.py test_fast     # только упавшие
python manage_project.py coverage      # с покрытием
```


=======
**96 тестов** — покрывают:

- AJAX contact (валидация, rate limit, tariff)
- CSRF (contact, vote, subscribe)
- Turnstile (success / failure / timeout / connection error / disabled)
- Blog vote (like / dislike / change / remove)
- Newsletter
- Scheduled posts (публикация в будущем)
- Subscribe + unsubscribe
- Базовые вьюхи (home, contact, blog)
- Admin smoke tests
- Contact notifications / Celery / transaction.on_commit
- PDF validation

---

## 📁 Структура

```
lynxreactor/
├── agency/                    # Основное приложение
│   ├── migrations/
│   ├── services/              # Email, Telegram, IndexNow
│   ├── management/commands/   # CLI-команды
│   ├── tests/                 # # pytest-тесты (96)
│   ├── admin.py
│   ├── models.py
│   ├── signals.py
│   ├── tasks.py
│   ├── views.py
│   └── ...
├── lynxreactor/               # Конфигурация проекта
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── celery.py
│   ├── urls.py
│   └── wsgi.py
├── templates/                 # HTML-шаблоны
├── static/                    # CSS, JS, изображения
├── locale/                    # Переводы (ru, en)
├── scripts/                   # Утилиты разработки
│   └── i18n/                  # Работа с .po / .mo
├── manage.py
├── manage_project.py          # Обёртка над manage.py
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
└── .env.example
```

---

## 🔐 Безопасность

- **CSRF:** все AJAX-endpoint'ы защищены (enforce_csrf_checks=True в тестах)
- **Turnstile:** Cloudflare Turnstile на всех публичных формах
- **Rate limit:** формы, голосования, подписки
- **PDF-валидация:** extension + %PDF- signature
- **Секреты:** только в .env — в git не попадают
- **Production:** check --deploy, HSTS, secure cookies

⚠️ Перед деплоем — [Django deployment checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/).

---

## 🌍 Двуязычность

**Структура:**
- `locale/ru/` — русские переводы
- `locale/en/` — английские переводы
- `.po` — исходники
- `.mo` — скомпилированные

**Workflow:**

```bash
python manage.py makemessages -l ru -l en
python scripts/i18n/translate_po.py --dry-run
python scripts/i18n/check_po.py
python manage.py compilemessages
```

---

## 🚀 Production deployment

1. **`.env.prod`** — секреты (SECRET_KEY, ALLOWED_HOSTS, DB, Redis, Email, Turnstile, Telegram)
2. **`DJANGO_SETTINGS_MODULE=lynxreactor.settings.prod`**
3. **PostgreSQL** — `DB_ENGINE=django.db.backends.postgresql`
4. **Redis** — `REDIS_URL=redis://localhost:6379/0`
5. **`python manage.py collectstatic`**
6. **`python manage.py migrate`**
7. **`python manage.py compilemessages`**
8. **Gunicorn** — `gunicorn lynxreactor.wsgi:application`
9. **Nginx** — прокси + static/media + X-Forwarded-For
10. **Celery worker** — `celery -A lynxreactor worker -l info`
11. **Celery beat** — `celery -A lynxreactor beat -l info`
12. **`python manage.py check --deploy`**

---

## 📝 Лицензия

**Proprietary.** Все права защищены.

Использование, копирование, распространение или модификация без письменного разрешения **LYNXREACTOR** запрещены.

См. `LICENSE`.

---

## 👥 Авторы

**LynxReactor** — [lynxreactor.by](https://lynxreactor.by)

---

**Made with ❤️ by LynxReactor Studio**

