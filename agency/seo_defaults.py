# agency/seo_defaults.py

"""
Дефолтные SEO-значения для страниц.

Используются как fallback, когда:
- запись PageSEO отсутствует в БД
- поля title/description/keywords пусты
- произошла ошибка конфигурации

После заполнения через админку — БД имеет приоритет.

============================================================
СТРУКТУРА
============================================================

АКТИВНЫЕ СТРАНИЦЫ (SEO выводится):
- home     → /              (главная)
- contact  → /contact/      (контакты, содержит секцию «О нас»)
- blog     → /blog/         (блог, список постов)

ЗАРЕЗЕРВИРОВАННЫЕ (SEO пока не выводится):
- portfolio → секция #portfolio на главной
- services  → секция #landing/#business/#refactor на главной
- pricing   → секция #pricing (тарифы) на главной
- about     → секция #about на /contact/

Эти ключи готовы к использованию, когда появятся отдельные URL.
============================================================
"""

SEO_PAGES = [
    ('home', 'Главная'),
    ('contact', 'Контакты'),
    ('blog', 'Блог'),
    # Зарезервированные:
    ('portfolio', 'Портфолио (секция главной)'),
    ('about', 'О нас (секция на /contact/)'),
    ('services', 'Услуги (секция главной)'),
    ('pricing', 'Тарифы (секция главной)'),
]


DEFAULT_SEO = {
    'home': {
        'ru': {
            'title': 'Разработка сайтов под ключ для бизнеса — LYNXREACTOR',
            'description': (
                'Разработка сайтов под ключ для бизнеса: лендинги, корпоративные сайты, '
                'интернет-магазины и веб-приложения. Уникальный дизайн, сложная '
                'функциональность, SEO и современные технологии Python и Django.'
            ),
            'keywords': (
                'разработка сайтов под ключ, создание сайтов под ключ, разработка сайтов, '
                'создание сайтов, разработка веб-сайтов, сайт для бизнеса, '
                'создание сайта для бизнеса, корпоративный сайт, разработка корпоративного сайта, '
                'лендинг, разработка лендинга, интернет-магазин, разработка интернет-магазина, '
                'веб-приложение, разработка веб-приложений, веб-разработка, '
                'SEO-оптимизация сайта, технический аудит сайта, аудит кода, рефакторинг, '
                'разработка на Python, разработка на Django, Python, Django, LYNXREACTOR'
            ),
        },
        'en': {
            'title': 'Custom Website Development for Business — LYNXREACTOR',
            'description': (
                'Custom website development for business: landing pages, corporate websites, '
                'online stores and web applications. Unique design, complex functionality, '
                'SEO and modern Python and Django technologies.'
            ),
            'keywords': (
                'custom website development, website development, web development, '
                'business website, corporate website, landing page, e-commerce, online store, '
                'web application, SEO optimization, technical audit, code audit, refactoring, '
                'Python development, Django development, Python, Django, LYNXREACTOR'
            ),
        },
    },
    'contact': {
        'ru': {
            'title': 'Контакты — LYNXREACTOR',
            'description': (
                'Свяжитесь с LYNXREACTOR для обсуждения разработки сайта или веб-приложения. '
                'Расскажите о задаче, получите консультацию и обсудите подходящее решение.'
            ),
            'keywords': (
                'контакты LYNXREACTOR, разработка сайтов контакты, заказать разработку сайта, '
                'заказать сайт, создание сайта под ключ, разработка сайта для бизнеса, '
                'разработчик сайтов, веб-разработка, Python разработка, Django разработка, '
                'LYNXREACTOR'
            ),
        },
        'en': {
            'title': 'Contact Us — LYNXREACTOR',
            'description': (
                'Contact LYNXREACTOR to discuss your website or web application development. '
                'Tell us about your project, get a consultation and find the right solution.'
            ),
            'keywords': (
                'contact LYNXREACTOR, website development contact, order website development, '
                'order website, custom website development, business website development, '
                'web developer, web development, Python development, Django development, '
                'LYNXREACTOR'
            ),
        },
    },
    'blog': {
        'ru': {
            'title': 'Блог о разработке сайтов и веб-технологиях — LYNXREACTOR',
            'description': (
                'Полезные статьи о разработке сайтов, веб-приложениях, SEO, производительности, '
                'безопасности, архитектуре и современных технологиях веб-разработки. '
                'Python и Django как основа технологического стека.'
            ),
            'keywords': (
                'блог о веб-разработке, разработка сайтов, создание сайтов, веб-разработка, '
                'SEO сайта, SEO-оптимизация, производительность сайта, безопасность сайта, '
                'архитектура веб-приложений, веб-приложения, Python, Django, JavaScript, '
                'рефакторинг, аудит кода, технический аудит сайта, LYNXREACTOR'
            ),
        },
        'en': {
            'title': 'Blog about Website Development and Web Technologies — LYNXREACTOR',
            'description': (
                'Useful articles about website development, web applications, SEO, performance, '
                'security, architecture and modern web technologies. '
                'Python and Django as the technology stack foundation.'
            ),
            'keywords': (
                'web development blog, website development, web development, '
                'SEO, SEO optimization, website performance, website security, '
                'web application architecture, web applications, Python, Django, JavaScript, '
                'refactoring, code audit, technical audit, LYNXREACTOR'
            ),
        },
    },
    'portfolio': {
        'ru': {
            'title': 'Портфолио — сайты и проекты LYNXREACTOR',
            'description': (
                'Проекты LYNXREACTOR: сайты для бизнеса, интернет-магазины, веб-приложения. '
                'Реальные кейсы, реализованные на Python/Django с уникальным дизайном.'
            ),
            'keywords': (
                'портфолио LYNXREACTOR, проекты веб-разработки, примеры сайтов, '
                'кейсы разработки сайтов, сайты для бизнеса, интернет-магазины, '
                'веб-приложения, Python, Django, LYNXREACTOR'
            ),
        },
        'en': {
            'title': 'Portfolio — Websites and Projects by LYNXREACTOR',
            'description': (
                'LYNXREACTOR projects: business websites, online stores, web applications. '
                'Real cases built with Python/Django and unique design.'
            ),
            'keywords': (
                'LYNXREACTOR portfolio, web development projects, website examples, '
                'website development cases, business websites, online stores, '
                'web applications, Python, Django, LYNXREACTOR'
            ),
        },
    },
    'about': {
        'ru': {
            'title': 'О студии LYNXREACTOR — команда веб-разработки',
            'description': (
                'LYNXREACTOR — команда веб-разработчиков, создающая сайты и веб-приложения '
                'на Python/Django. Индивидуальный подход, современные технологии, '
                'качественный код и поддержка проектов.'
            ),
            'keywords': (
                'о студии LYNXREACTOR, команда веб-разработки, веб-студия, разработчики сайтов, '
                'Python разработчики, Django разработчики, веб-разработка, LYNXREACTOR'
            ),
        },
        'en': {
            'title': 'About LYNXREACTOR — Web Development Team',
            'description': (
                'LYNXREACTOR is a team of web developers building websites and web applications '
                'with Python/Django. Individual approach, modern technologies, '
                'quality code and project support.'
            ),
            'keywords': (
                'about LYNXREACTOR, web development team, web studio, website developers, '
                'Python developers, Django developers, web development, LYNXREACTOR'
            ),
        },
    },
    'services': {
        'ru': {
            'title': 'Услуги — разработка сайтов и веб-приложений | LYNXREACTOR',
            'description': (
                'Полный спектр услуг по разработке: лендинги, корпоративные сайты, '
                'интернет-магазины, веб-приложения, рефакторинг, аудит безопасности '
                'и производительности.'
            ),
            'keywords': (
                'услуги разработки сайтов, разработка лендинга, разработка интернет-магазина, '
                'разработка веб-приложения, рефакторинг кода, аудит безопасности сайта, '
                'аудит производительности, веб-разработка, Python, Django, LYNXREACTOR'
            ),
        },
        'en': {
            'title': 'Services — Website and Web Application Development | LYNXREACTOR',
            'description': (
                'Full range of development services: landing pages, corporate websites, '
                'online stores, web applications, refactoring, security and performance audit.'
            ),
            'keywords': (
                'website development services, landing page development, e-commerce development, '
                'web application development, code refactoring, website security audit, '
                'performance audit, web development, Python, Django, LYNXREACTOR'
            ),
        },
    },
    'pricing': {
        'ru': {
            'title': 'Тарифы на разработку сайтов — LYNXREACTOR',
            'description': (
                'Прозрачные тарифы на разработку сайтов под ключ: лендинг, корпоративный сайт, '
                'интернет-магазин и индивидуальные проекты. Стоимость и сроки.'
            ),
            'keywords': (
                'тарифы разработки сайтов, стоимость разработки сайта, цена сайта, '
                'сколько стоит сайт, разработка сайта под ключ цена, тарифы LYNXREACTOR, '
                'заказать сайт, Python, Django, LYNXREACTOR'
            ),
        },
        'en': {
            'title': 'Website Development Pricing — LYNXREACTOR',
            'description': (
                'Transparent pricing for turnkey website development: landing page, corporate website, '
                'online store and custom projects. Cost and timeline.'
            ),
            'keywords': (
                'website development pricing, website cost, website price, '
                'how much does a website cost, turnkey website development price, LYNXREACTOR pricing, '
                'order website, Python, Django, LYNXREACTOR'
            ),
        },
    },
}


def get_default_seo(page_key, lang='ru'):
    lang = (lang or 'ru').split('-')[0]
    if lang not in ('ru', 'en'):
        lang = 'ru'
    page_data = DEFAULT_SEO.get(page_key, {})
    lang_data = page_data.get(lang) or page_data.get('ru', {})
    if not lang_data:
        return {
            'title': 'LYNXREACTOR — Разработка сайтов',
            'description': 'Разработка сайтов и веб-приложений на Python/Django.',
            'keywords': 'LYNXREACTOR, разработка сайтов, веб-разработка',
        }
    return {
        'title': lang_data.get('title', ''),
        'description': lang_data.get('description', ''),
        'keywords': lang_data.get('keywords', ''),
    }


def get_page_label(page_key):
    for key, label in SEO_PAGES:
        if key == page_key:
            return label
    return page_key