# agency/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.utils.text import slugify
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit, ResizeToFill
from ckeditor.fields import RichTextField
from .validators import (
    validate_features,
    validate_technologies,
    validate_tags,
    validate_pdf_file,
)


# ============================================================
# БАЗОВЫЕ МОДЕЛИ
# ============================================================

class BaseModel(models.Model):
    """Абстрактная базовая модель с общими полями"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Date created"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Date updated"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))

    class Meta:
        abstract = True
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.__class__.__name__} #{self.id}"


# ============================================================
# HERO SECTION
# ============================================================

class HeroSection(models.Model):
    """Hero секция для каждой страницы"""
    PAGE_CHOICES = [
        ('home', _('Home')),
        ('contacts', _('Contacts')),
        ('blog', _('Blog')),
    ]

    page = models.CharField(
        max_length=20, choices=PAGE_CHOICES, unique=True,
        verbose_name=_("Page")
    )
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    subtitle = models.CharField(max_length=300, blank=True, default='', verbose_name=_("Subtitle"))
    description = models.TextField(verbose_name=_("Description"))

    # 4 изображения для разных комбинаций темы и языка
    hero_image_light_ru = models.ImageField(
        upload_to='hero/light/ru/', blank=True, null=True,
        verbose_name=_("Hero Image Light + RU")
    )
    hero_image_light_en = models.ImageField(
        upload_to='hero/light/en/', blank=True, null=True,
        verbose_name=_("Hero Image Light + EN")
    )
    hero_image_dark_ru = models.ImageField(
        upload_to='hero/dark/ru/', blank=True, null=True,
        verbose_name=_("Hero Image Dark + RU")
    )
    hero_image_dark_en = models.ImageField(
        upload_to='hero/dark/en/', blank=True, null=True,
        verbose_name=_("Hero Image Dark + EN")
    )

    # Миниатюры
    hero_image_light_ru_thumbnail = ImageSpecField(
        source='hero_image_light_ru',
        processors=[ResizeToFill(1920, 1080)],
        format='WEBP', options={'quality': 85}
    )
    hero_image_light_en_thumbnail = ImageSpecField(
        source='hero_image_light_en',
        processors=[ResizeToFill(1920, 1080)],
        format='WEBP', options={'quality': 85}
    )
    hero_image_dark_ru_thumbnail = ImageSpecField(
        source='hero_image_dark_ru',
        processors=[ResizeToFill(1920, 1080)],
        format='WEBP', options={'quality': 85}
    )
    hero_image_dark_en_thumbnail = ImageSpecField(
        source='hero_image_dark_en',
        processors=[ResizeToFill(1920, 1080)],
        format='WEBP', options={'quality': 85}
    )

    # Кнопки
    cta_text = models.CharField(max_length=50, blank=True, default='', verbose_name=_("Button text"))
    cta_url = models.CharField(max_length=200, blank=True, default='', verbose_name=_("Button URL"))
    secondary_cta_text = models.CharField(
        max_length=50, blank=True, default='',
        verbose_name=_("Secondary button text")
    )
    secondary_cta_url = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name=_("Secondary button URL")
    )

    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    class Meta:
        verbose_name = _("Hero Section")
        verbose_name_plural = _("Hero Sections")

    def __str__(self):
        return f"{self.get_page_display()} - Hero"

    def get_hero_image(self, theme='light', language='ru'):
        field_name = f"hero_image_{theme}_{language}"
        image = getattr(self, field_name, None)
        if not image:
            if theme == 'dark' and language == 'en':
                fallback = self.hero_image_dark_ru or self.hero_image_light_en or self.hero_image_light_ru
            elif theme == 'dark':
                fallback = self.hero_image_dark_ru or self.hero_image_light_ru
            elif language == 'en':
                fallback = self.hero_image_light_en or self.hero_image_light_ru
            else:
                fallback = self.hero_image_light_ru
            return fallback
        return image

    def get_hero_image_url(self, theme='light', language='ru'):
        image = self.get_hero_image(theme, language)
        return image.url if image else None

    def get_hero_image_thumbnail(self, theme='light', language='ru'):
        thumbnail_field = f"hero_image_{theme}_{language}_thumbnail"
        thumbnail = getattr(self, thumbnail_field, None)
        return thumbnail if thumbnail else self.get_hero_image(theme, language)


# ============================================================
# SERVICES SECTION
# ============================================================

class ServicesSection(BaseModel):
    title = models.CharField(max_length=200, verbose_name=_("Section Title"))
    subtitle = models.CharField(max_length=300, blank=True, default='', verbose_name=_("Subtitle"))
    description = models.TextField(blank=True, default='', verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Services Section")
        verbose_name_plural = _("Services Sections")

    def __str__(self):
        return self.title


class ServiceItem(BaseModel):
    section = models.ForeignKey(
        ServicesSection, on_delete=models.CASCADE,
        related_name='services', verbose_name=_("Services Section")
    )
    number = models.PositiveIntegerField(default=1, verbose_name=_("Number"))
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    description = models.TextField(verbose_name=_("Description"))
    icon = models.CharField(
        max_length=50, blank=True, default='fa-rocket',
        verbose_name=_("Icon (CSS class)")
    )

    image_light_ru = models.ImageField(
        upload_to='services/light/ru/', blank=True, null=True,
        verbose_name=_("Image Light + RU")
    )
    image_light_en = models.ImageField(
        upload_to='services/light/en/', blank=True, null=True,
        verbose_name=_("Image Light + EN")
    )
    image_dark_ru = models.ImageField(
        upload_to='services/dark/ru/', blank=True, null=True,
        verbose_name=_("Image Dark + RU")
    )
    image_dark_en = models.ImageField(
        upload_to='services/dark/en/', blank=True, null=True,
        verbose_name=_("Image Dark + EN")
    )

    image_light_ru_thumbnail = ImageSpecField(
        source='image_light_ru', processors=[ResizeToFill(800, 600)],
        format='WEBP', options={'quality': 85}
    )
    image_light_en_thumbnail = ImageSpecField(
        source='image_light_en', processors=[ResizeToFill(800, 600)],
        format='WEBP', options={'quality': 85}
    )
    image_dark_ru_thumbnail = ImageSpecField(
        source='image_dark_ru', processors=[ResizeToFill(800, 600)],
        format='WEBP', options={'quality': 85}
    )
    image_dark_en_thumbnail = ImageSpecField(
        source='image_dark_en', processors=[ResizeToFill(800, 600)],
        format='WEBP', options={'quality': 85}
    )

    url = models.CharField(max_length=200, blank=True, default='', verbose_name=_("URL"))

    class Meta:
        verbose_name = _("Service Item")
        verbose_name_plural = _("Service Items")
        ordering = ['order', 'number']

    def __str__(self):
        return f"{self.number}. {self.title}"

    def get_image_for_theme_lang(self, theme='light', language='ru'):
        field_name = f"image_{theme}_{language}"
        image = getattr(self, field_name, None)
        return image if image else self.image_light_ru

    def get_image_url_for_theme_lang(self, theme='light', language='ru'):
        image = self.get_image_for_theme_lang(theme, language)
        return image.url if image else None


# ============================================================
# TECH SECTION
# ============================================================

class TechSection(BaseModel):
    title = models.CharField(max_length=200, verbose_name=_("Section Title"))
    subtitle = models.CharField(max_length=300, blank=True, default='', verbose_name=_("Subtitle"))
    description = models.TextField(blank=True, default='', verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Tech Section")
        verbose_name_plural = _("Tech Sections")

    def __str__(self):
        return self.title


class TechItem(BaseModel):
    CATEGORY_CHOICES = [
        ('backend', _('Backend')),
        ('frontend', _('Frontend')),
        ('database', _('Database')),
        ('devops', _('DevOps')),
        ('other', _('Other')),
    ]

    section = models.ForeignKey(
        TechSection, on_delete=models.CASCADE,
        related_name='technologies', verbose_name=_("Tech Section")
    )
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default='backend',
        verbose_name=_("Category")
    )
    is_primary = models.BooleanField(default=False, verbose_name=_("Primary tech"))

    logo = models.ImageField(
        upload_to='tech/', blank=True, null=True, verbose_name=_("Logo")
    )
    logo_thumbnail = ImageSpecField(
        source='logo', processors=[ResizeToFill(100, 100)],
        format='WEBP', options={'quality': 85}
    )

    description = models.TextField(blank=True, default='', verbose_name=_("Description"))
    url = models.URLField(blank=True, default='', verbose_name=_("URL"))

    class Meta:
        verbose_name = _("Tech Item")
        verbose_name_plural = _("Tech Items")
        ordering = ['order']

    def __str__(self):
        return self.name


# ============================================================
# LANDING SECTION
# ============================================================

class LandingSection(BaseModel):
    label_ru = models.CharField(max_length=50, default='ЛЕНДИНГИ', verbose_name=_("Label RU"))
    label_en = models.CharField(max_length=50, default='LANDING PAGES', verbose_name=_("Label EN"))
    title_ru = models.CharField(
        max_length=200, default='Разработка продающих лендингов под ключ',
        verbose_name=_("Title RU")
    )
    title_en = models.CharField(
        max_length=200, default='Development of high-converting landing pages',
        verbose_name=_("Title EN")
    )
    description_ru = models.TextField(
        default='Создаём стильные одностраничные сайты, которые фокусируют внимание, '
                'вызывают доверие и превращают посетителей в клиентов.',
        verbose_name=_("Description RU")
    )
    description_en = models.TextField(
        default='We create stylish one-page websites that focus attention, '
                'build trust and turn visitors into customers.',
        verbose_name=_("Description EN")
    )

    image_light_ru = models.ImageField(
        upload_to='landing/light/ru/', blank=True, null=True, verbose_name=_("Image Light + RU")
    )
    image_light_en = models.ImageField(
        upload_to='landing/light/en/', blank=True, null=True, verbose_name=_("Image Light + EN")
    )
    image_dark_ru = models.ImageField(
        upload_to='landing/dark/ru/', blank=True, null=True, verbose_name=_("Image Dark + RU")
    )
    image_dark_en = models.ImageField(
        upload_to='landing/dark/en/', blank=True, null=True, verbose_name=_("Image Dark + EN")
    )

    image_light_ru_thumbnail = ImageSpecField(
        source='image_light_ru', processors=[ResizeToFill(800, 500)],
        format='WEBP', options={'quality': 85}
    )
    image_light_en_thumbnail = ImageSpecField(
        source='image_light_en', processors=[ResizeToFill(800, 500)],
        format='WEBP', options={'quality': 85}
    )
    image_dark_ru_thumbnail = ImageSpecField(
        source='image_dark_ru', processors=[ResizeToFill(800, 500)],
        format='WEBP', options={'quality': 85}
    )
    image_dark_en_thumbnail = ImageSpecField(
        source='image_dark_en', processors=[ResizeToFill(800, 500)],
        format='WEBP', options={'quality': 85}
    )

    cta_text_ru = models.CharField(max_length=50, default='Заказать лендинг', verbose_name=_("Button text RU"))
    cta_text_en = models.CharField(max_length=50, default='Order Landing', verbose_name=_("Button text EN"))
    cta_url = models.CharField(max_length=200, default="/contacts/", verbose_name=_("Button URL"))

    class Meta:
        verbose_name = _("Landing Section")
        verbose_name_plural = _("Landing Sections")

    def __str__(self):
        return self.title_ru or "Landing Section"

    @staticmethod
    def _get_lang(lang):
        if lang is None:
            from django.utils.translation import get_language
            lang = get_language() or 'ru'
        return lang.split('-')[0]

    def get_title(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'title_{lang}', self.title_ru)

    def get_description(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'description_{lang}', self.description_ru)

    def get_label(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'label_{lang}', self.label_ru)

    def get_cta_text(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'cta_text_{lang}', self.cta_text_ru)

    def get_image_for_theme_lang(self, theme='light', language='ru'):
        field_name = f"image_{theme}_{language}"
        image = getattr(self, field_name, None)
        return image if image else self.image_light_ru


class LandingFeature(BaseModel):
    section = models.ForeignKey(
        LandingSection, on_delete=models.CASCADE,
        related_name='features', verbose_name=_("Landing Section")
    )
    icon = models.CharField(max_length=50, default='fa-check', verbose_name=_("Icon"))
    title_ru = models.CharField(max_length=100, default='Фокус на продажах', verbose_name=_("Title RU"))
    title_en = models.CharField(max_length=100, default='Focus on sales', verbose_name=_("Title EN"))
    description_ru = models.CharField(max_length=200, default='Максимальная конверсия', verbose_name=_("Description RU"))
    description_en = models.CharField(max_length=200, default='Maximum conversion', verbose_name=_("Description EN"))

    class Meta:
        verbose_name = _("Landing Feature")
        verbose_name_plural = _("Landing Features")
        ordering = ['order']

    def __str__(self):
        return self.title_ru or "Landing Feature"

    @staticmethod
    def _get_lang(lang):
        if lang is None:
            from django.utils.translation import get_language
            lang = get_language() or 'ru'
        return lang.split('-')[0]

    def get_title(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'title_{lang}', self.title_ru)

    def get_description(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'description_{lang}', self.description_ru)


class LandingDetail(BaseModel):
    section = models.ForeignKey(
        LandingSection, on_delete=models.CASCADE,
        related_name='details', verbose_name=_("Landing Section")
    )
    icon = models.CharField(max_length=50, default='fa-search', verbose_name=_("Icon"))
    title_ru = models.CharField(max_length=100, default='Анализ целевой аудитории', verbose_name=_("Title RU"))
    title_en = models.CharField(max_length=100, default='Target audience analysis', verbose_name=_("Title EN"))
    description_ru = models.CharField(max_length=200, default='Глубокое исследование вашей ЦА', verbose_name=_("Description RU"))
    description_en = models.CharField(max_length=200, default='In-depth research of your target audience', verbose_name=_("Description EN"))

    class Meta:
        verbose_name = _("Landing Detail")
        verbose_name_plural = _("Landing Details")
        ordering = ['order']

    def __str__(self):
        return self.title_ru or "Landing Detail"

    @staticmethod
    def _get_lang(lang):
        if lang is None:
            from django.utils.translation import get_language
            lang = get_language() or 'ru'
        return lang.split('-')[0]

    def get_title(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'title_{lang}', self.title_ru)

    def get_description(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'description_{lang}', self.description_ru)


# ============================================================
# BUSINESS SECTION
# ============================================================

class BusinessSection(BaseModel):
    label_ru = models.CharField(max_length=50, default='ИНТЕРНЕТ-МАГАЗИНЫ', verbose_name=_("Label RU"))
    label_en = models.CharField(max_length=50, default='E-COMMERCE', verbose_name=_("Label EN"))
    title_ru = models.CharField(
        max_length=200, default='Сайт для бизнеса, который продаёт', verbose_name=_("Title RU")
    )
    title_en = models.CharField(
        max_length=200, default='A website for business that sells', verbose_name=_("Title EN")
    )
    description_ru = models.TextField(
        default='Создаём интернет-магазины и корпоративные сайты с продуманной структурой, '
                'удобной админ-панелью и полной интеграцией с системами оплаты.',
        verbose_name=_("Description RU")
    )
    description_en = models.TextField(
        default='We create online stores and corporate websites with a well-thought-out '
                'structure, a convenient admin panel and full integration with payment systems.',
        verbose_name=_("Description EN")
    )

    image_light_ru = models.ImageField(
        upload_to='business/light/ru/', blank=True, null=True, verbose_name=_("Image Light + RU")
    )
    image_light_en = models.ImageField(
        upload_to='business/light/en/', blank=True, null=True, verbose_name=_("Image Light + EN")
    )
    image_dark_ru = models.ImageField(
        upload_to='business/dark/ru/', blank=True, null=True, verbose_name=_("Image Dark + RU")
    )
    image_dark_en = models.ImageField(
        upload_to='business/dark/en/', blank=True, null=True, verbose_name=_("Image Dark + EN")
    )

    image_light_ru_thumbnail = ImageSpecField(
        source='image_light_ru', processors=[ResizeToFill(800, 500)],
        format='WEBP', options={'quality': 85}
    )
    image_light_en_thumbnail = ImageSpecField(
        source='image_light_en', processors=[ResizeToFill(800, 500)],
        format='WEBP', options={'quality': 85}
    )
    image_dark_ru_thumbnail = ImageSpecField(
        source='image_dark_ru', processors=[ResizeToFill(800, 500)],
        format='WEBP', options={'quality': 85}
    )
    image_dark_en_thumbnail = ImageSpecField(
        source='image_dark_en', processors=[ResizeToFill(800, 500)],
        format='WEBP', options={'quality': 85}
    )

    cta_text_ru = models.CharField(max_length=50, default='Заказать сайт', verbose_name=_("Button text RU"))
    cta_text_en = models.CharField(max_length=50, default='Order Site', verbose_name=_("Button text EN"))
    cta_url = models.CharField(max_length=200, default="/contacts/", verbose_name=_("Button URL"))

    class Meta:
        verbose_name = _("Business Section")
        verbose_name_plural = _("Business Sections")

    def __str__(self):
        return self.title_ru or "Business Section"

    @staticmethod
    def _get_lang(lang):
        if lang is None:
            from django.utils.translation import get_language
            lang = get_language() or 'ru'
        return lang.split('-')[0]

    def get_title(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'title_{lang}', self.title_ru)

    def get_description(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'description_{lang}', self.description_ru)

    def get_label(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'label_{lang}', self.label_ru)

    def get_cta_text(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'cta_text_{lang}', self.cta_text_ru)

    def get_image_for_theme_lang(self, theme='light', language='ru'):
        field_name = f"image_{theme}_{language}"
        image = getattr(self, field_name, None)
        return image if image else self.image_light_ru


class BusinessFeature(BaseModel):
    section = models.ForeignKey(
        BusinessSection, on_delete=models.CASCADE,
        related_name='features', verbose_name=_("Business Section")
    )
    icon = models.CharField(max_length=50, default='fa-check', verbose_name=_("Icon"))
    title_ru = models.CharField(max_length=100, default='Интернет-магазин', verbose_name=_("Title RU"))
    title_en = models.CharField(max_length=100, default='Online store', verbose_name=_("Title EN"))
    description_ru = models.CharField(max_length=200, default='Полноценная онлайн-торговля', verbose_name=_("Description RU"))
    description_en = models.CharField(max_length=200, default='Full-fledged online trading', verbose_name=_("Description EN"))

    class Meta:
        verbose_name = _("Business Feature")
        verbose_name_plural = _("Business Features")
        ordering = ['order']

    def __str__(self):
        return self.title_ru or "Business Feature"

    @staticmethod
    def _get_lang(lang):
        if lang is None:
            from django.utils.translation import get_language
            lang = get_language() or 'ru'
        return lang.split('-')[0]

    def get_title(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'title_{lang}', self.title_ru)

    def get_description(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'description_{lang}', self.description_ru)


class BusinessDetail(BaseModel):
    section = models.ForeignKey(
        BusinessSection, on_delete=models.CASCADE,
        related_name='details', verbose_name=_("Business Section")
    )
    icon = models.CharField(max_length=50, default='fa-search', verbose_name=_("Icon"))
    title_ru = models.CharField(max_length=100, default='Каталог товаров', verbose_name=_("Title RU"))
    title_en = models.CharField(max_length=100, default='Product catalog', verbose_name=_("Title EN"))
    description_ru = models.CharField(max_length=200, default='Удобная структура каталога', verbose_name=_("Description RU"))
    description_en = models.CharField(max_length=200, default='Convenient catalog structure', verbose_name=_("Description EN"))

    class Meta:
        verbose_name = _("Business Detail")
        verbose_name_plural = _("Business Details")
        ordering = ['order']

    def __str__(self):
        return self.title_ru or "Business Detail"

    @staticmethod
    def _get_lang(lang):
        if lang is None:
            from django.utils.translation import get_language
            lang = get_language() or 'ru'
        return lang.split('-')[0]

    def get_title(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'title_{lang}', self.title_ru)

    def get_description(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'description_{lang}', self.description_ru)


# ============================================================
# REFACTOR SECTION
# ============================================================

class RefactorSection(BaseModel):
    label_ru = models.CharField(max_length=50, default='РЕФАКТОРИНГ И АУДИТ', verbose_name=_("Label RU"))
    label_en = models.CharField(max_length=50, default='REFACTORING & AUDIT', verbose_name=_("Label EN"))
    title_ru = models.CharField(
        max_length=200,
        default='Аудит безопасности и производительности вашего Django-проекта',
        verbose_name=_("Title RU")
    )
    title_en = models.CharField(
        max_length=200,
        default='Security and performance audit of your Django project',
        verbose_name=_("Title EN")
    )
    description_ru = models.TextField(
        default='Проводим глубокий аудит кода, архитектуры и безопасности. '
                'Выявляем узкие места, исправляем ошибки и оптимизируем производительность.',
        verbose_name=_("Description RU")
    )
    description_en = models.TextField(
        default='We conduct a deep audit of code, architecture and security. '
                'We identify bottlenecks, fix errors and optimize performance.',
        verbose_name=_("Description EN")
    )

    image_light_ru = models.ImageField(
        upload_to='refactor/light/ru/', blank=True, null=True, verbose_name=_("Image Light + RU")
    )
    image_light_en = models.ImageField(
        upload_to='refactor/light/en/', blank=True, null=True, verbose_name=_("Image Light + EN")
    )
    image_dark_ru = models.ImageField(
        upload_to='refactor/dark/ru/', blank=True, null=True, verbose_name=_("Image Dark + RU")
    )
    image_dark_en = models.ImageField(
        upload_to='refactor/dark/en/', blank=True, null=True, verbose_name=_("Image Dark + EN")
    )

    image_light_ru_thumbnail = ImageSpecField(
        source='image_light_ru', processors=[ResizeToFill(800, 500)],
        format='WEBP', options={'quality': 85}
    )
    image_light_en_thumbnail = ImageSpecField(
        source='image_light_en', processors=[ResizeToFill(800, 500)],
        format='WEBP', options={'quality': 85}
    )
    image_dark_ru_thumbnail = ImageSpecField(
        source='image_dark_ru', processors=[ResizeToFill(800, 500)],
        format='WEBP', options={'quality': 85}
    )
    image_dark_en_thumbnail = ImageSpecField(
        source='image_dark_en', processors=[ResizeToFill(800, 500)],
        format='WEBP', options={'quality': 85}
    )

    cta_text_ru = models.CharField(max_length=50, default='Заказать аудит', verbose_name=_("Button text RU"))
    cta_text_en = models.CharField(max_length=50, default='Order Audit', verbose_name=_("Button text EN"))
    cta_url = models.CharField(max_length=200, default="/contacts/", verbose_name=_("Button URL"))

    class Meta:
        verbose_name = _("Refactor Section")
        verbose_name_plural = _("Refactor Sections")

    def __str__(self):
        return self.title_ru or "Refactor Section"

    @staticmethod
    def _get_lang(lang):
        if lang is None:
            from django.utils.translation import get_language
            lang = get_language() or 'ru'
        return lang.split('-')[0]

    def get_title(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'title_{lang}', self.title_ru)

    def get_description(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'description_{lang}', self.description_ru)

    def get_label(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'label_{lang}', self.label_ru)

    def get_cta_text(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'cta_text_{lang}', self.cta_text_ru)

    def get_image_for_theme_lang(self, theme='light', language='ru'):
        field_name = f"image_{theme}_{language}"
        image = getattr(self, field_name, None)
        return image if image else self.image_light_ru


class RefactorFeature(BaseModel):
    section = models.ForeignKey(
        RefactorSection, on_delete=models.CASCADE,
        related_name='features', verbose_name=_("Refactor Section")
    )
    icon = models.CharField(max_length=50, default='fa-shield-alt', verbose_name=_("Icon"))
    text_ru = models.CharField(max_length=100, default='Безопасность', verbose_name=_("Text RU"))
    text_en = models.CharField(max_length=100, default='Security', verbose_name=_("Text EN"))

    class Meta:
        verbose_name = _("Refactor Feature")
        verbose_name_plural = _("Refactor Features")
        ordering = ['order']

    def __str__(self):
        return self.text_ru or "Refactor Feature"

    @staticmethod
    def _get_lang(lang):
        if lang is None:
            from django.utils.translation import get_language
            lang = get_language() or 'ru'
        return lang.split('-')[0]

    def get_text(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'text_{lang}', self.text_ru)


class RefactorDetail(BaseModel):
    section = models.ForeignKey(
        RefactorSection, on_delete=models.CASCADE,
        related_name='details', verbose_name=_("Refactor Section")
    )
    icon = models.CharField(max_length=50, default='fa-search', verbose_name=_("Icon"))
    title_ru = models.CharField(max_length=100, default='Аудит кода', verbose_name=_("Title RU"))
    title_en = models.CharField(max_length=100, default='Code audit', verbose_name=_("Title EN"))
    description_ru = models.CharField(max_length=200, default='Проверка качества кода и поиск уязвимостей', verbose_name=_("Description RU"))
    description_en = models.CharField(max_length=200, default='Code quality check and vulnerability search', verbose_name=_("Description EN"))

    class Meta:
        verbose_name = _("Refactor Detail")
        verbose_name_plural = _("Refactor Details")
        ordering = ['order']

    def __str__(self):
        return self.title_ru or "Refactor Detail"

    @staticmethod
    def _get_lang(lang):
        if lang is None:
            from django.utils.translation import get_language
            lang = get_language() or 'ru'
        return lang.split('-')[0]

    def get_title(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'title_{lang}', self.title_ru)

    def get_description(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'description_{lang}', self.description_ru)


# ============================================================
# PORTFOLIO SECTION
# ============================================================

class PortfolioSection(BaseModel):
    subtitle_ru = models.CharField(max_length=300, default='НАШИ РАБОТЫ', verbose_name=_("Subtitle RU"))
    subtitle_en = models.CharField(max_length=300, default='OUR WORKS', verbose_name=_("Subtitle EN"))
    title_ru = models.CharField(max_length=200, default='Сайты, которыми мы гордимся', verbose_name=_("Title RU"))
    title_en = models.CharField(max_length=200, default='Websites we are proud of', verbose_name=_("Title EN"))
    description_ru = models.TextField(default='Смотрите наши проекты и кейсы', verbose_name=_("Description RU"))
    description_en = models.TextField(default='View our projects and case studies', verbose_name=_("Description EN"))

    class Meta:
        verbose_name = _("Portfolio Section")
        verbose_name_plural = _("Portfolio Sections")

    def __str__(self):
        return self.title_ru or "Portfolio Section"

    @staticmethod
    def _get_lang(lang):
        if lang is None:
            from django.utils.translation import get_language
            lang = get_language() or 'ru'
        return lang.split('-')[0]

    def get_subtitle(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'subtitle_{lang}', self.subtitle_ru)

    def get_title(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'title_{lang}', self.title_ru)

    def get_description(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'description_{lang}', self.description_ru)


class PortfolioItem(BaseModel):
    section = models.ForeignKey(
        PortfolioSection, on_delete=models.CASCADE,
        related_name='items', verbose_name=_("Portfolio Section")
    )
    title_ru = models.CharField(max_length=200, default='Название проекта', verbose_name=_("Title RU"))
    title_en = models.CharField(max_length=200, default='Project name', verbose_name=_("Title EN"))
    slug = models.SlugField(unique=True, blank=True, verbose_name=_("URL slug"))
    category_ru = models.CharField(max_length=100, blank=True, default='Разработка', verbose_name=_("Category RU"))
    category_en = models.CharField(max_length=100, blank=True, default='Development', verbose_name=_("Category EN"))

    main_image_light = models.ImageField(
        upload_to='portfolio/light/', blank=True, null=True, verbose_name=_("Main image Light Theme")
    )
    main_image_dark = models.ImageField(
        upload_to='portfolio/dark/', blank=True, null=True, verbose_name=_("Main image Dark Theme")
    )

    main_image_light_thumbnail = ImageSpecField(
        source='main_image_light', processors=[ResizeToFill(600, 400)],
        format='WEBP', options={'quality': 85}
    )
    main_image_dark_thumbnail = ImageSpecField(
        source='main_image_dark', processors=[ResizeToFill(600, 400)],
        format='WEBP', options={'quality': 85}
    )

    description_ru = models.TextField(blank=True, default='Описание проекта', verbose_name=_("Description RU"))
    description_en = models.TextField(blank=True, default='Project description', verbose_name=_("Description EN"))
    client_name = models.CharField(max_length=100, blank=True, default='', verbose_name=_("Client"))
    project_url = models.URLField(blank=True, default='', verbose_name=_("Project URL"))
    technologies = models.JSONField(default=list, blank=True, validators=[validate_technologies], verbose_name=_("Technologies"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Featured"))

    # SEO (ручной ввод RU/EN)
    seo_title_ru = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name=_("SEO Title (RU)"),
        help_text=_("Если пусто — используется SEO раздела «Портфолио»")
    )
    seo_title_en = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name=_("SEO Title (EN)"),
        help_text=_("Если пусто — используется SEO раздела «Портфолио»")
    )
    seo_description_ru = models.CharField(
        max_length=500, blank=True, default='',
        verbose_name=_("SEO Description (RU)"),
        help_text=_("Если пусто — используется SEO раздела «Портфолио»")
    )
    seo_description_en = models.CharField(
        max_length=500, blank=True, default='',
        verbose_name=_("SEO Description (EN)"),
        help_text=_("Если пусто — используется SEO раздела «Портфолио»")
    )

    class Meta:
        verbose_name = _("Portfolio Item")
        verbose_name_plural = _("Portfolio Items")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at'], name='portfolio_created_idx'),
            models.Index(fields=['is_featured', 'is_active'], name='portfolio_featured_idx'),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title_ru or self.title_en or 'project')
        if self.technologies is None:
            self.technologies = []
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_ru or self.title_en or "Portfolio Item"

    @staticmethod
    def _get_lang(lang):
        if lang is None:
            from django.utils.translation import get_language
            lang = get_language() or 'ru'
        return lang.split('-')[0]

    def get_title(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'title_{lang}', self.title_ru)

    def get_category(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'category_{lang}', self.category_ru)

    def get_description(self, lang=None):
        lang = self._get_lang(lang)
        return getattr(self, f'description_{lang}', self.description_ru)

    def get_main_image_for_theme(self, theme='light'):
        if theme == 'dark' and self.main_image_dark:
            return self.main_image_dark_thumbnail or self.main_image_dark
        return self.main_image_light_thumbnail or self.main_image_light

    def get_seo_title(self, lang=None):
        lang = self._get_lang(lang)
        value = getattr(self, f'seo_title_{lang}', '') or ''
        if value.strip():
            return value.strip()
        if lang != 'ru':
            value_ru = self.seo_title_ru or ''
            if value_ru.strip():
                return value_ru.strip()
        return ''

    def get_seo_description(self, lang=None):
        lang = self._get_lang(lang)
        value = getattr(self, f'seo_description_{lang}', '') or ''
        if value.strip():
            return value.strip()
        if lang != 'ru':
            value_ru = self.seo_description_ru or ''
            if value_ru.strip():
                return value_ru.strip()
        return ''


# ============================================================
# ТАРИФЫ
# ============================================================

class Tariff(BaseModel):
    name = models.CharField(max_length=100, verbose_name=_("Tariff name"))
    slug = models.SlugField(unique=True, blank=True, verbose_name=_("URL slug"))

    site_format = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name=_("Site format"),
        help_text=_("For example: LANDING / LANDING PAGE")
    )
    subtitle = models.CharField(
        max_length=300, blank=True, default='',
        verbose_name=_("Subtitle"),
        help_text=_("Brief description of the tariff (1-2 sentences)")
    )
    description = models.TextField(blank=True, default='', verbose_name=_("Description"))

    price_byn = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Price (BYN)"))
    price_rub = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Price (RUB)"))
    price_eur = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Price (EUR)"))
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Price (USD)"))

    development_time = models.CharField(
        max_length=100, default=_("Individual"),
        verbose_name=_("Development time (RU)")
    )
    development_time_en = models.CharField(
        max_length=100, blank=True, default='',
        verbose_name=_("Development time (EN)"),
        help_text=_("Leave empty to use the Russian version")
    )

    features = models.JSONField(
        default=dict, blank=True,
        validators=[validate_features],
        verbose_name=_("Tariff features"),
        help_text=_('{"ru": ["Особенность 1"], "en": ["Feature 1"]}')
    )

    is_popular = models.BooleanField(default=False, verbose_name=_("Popular tariff"))
    is_custom = models.BooleanField(default=False, verbose_name=_("Custom tariff"))

    icon = models.CharField(
        max_length=50, blank=True, default='fa-rocket',
        verbose_name=_("Icon"),
        help_text=_("Font Awesome icon, e.g.: fa-rocket, fa-store, fa-crown")
    )
    accent_color = models.CharField(
        max_length=20, blank=True, default='gold',
        verbose_name=_("Accent color"),
        help_text=_("gold, blue, green, purple, orange, red")
    )

    class Meta:
        verbose_name = _("Tariff")
        verbose_name_plural = _("Tariffs")
        ordering = ['order']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or f"tariff-{self.id or 'new'}"
            counter = 1
            new_slug = base_slug
            while Tariff.objects.filter(slug=new_slug).exclude(id=self.id).exists():
                new_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = new_slug
        if self.features is None:
            self.features = {}
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_price_display(self, currency='byn'):
        price_map = {'byn': self.price_byn, 'rub': self.price_rub, 'eur': self.price_eur, 'usd': self.price_usd}
        price = price_map.get(currency)
        if price is None:
            return None
        return f"от {int(price)}" if price % 1 == 0 else f"от {price:.2f}"

    def get_features(self, lang=None):
        if lang is None:
            from django.utils.translation import get_language
            lang = get_language() or 'ru'
        lang = lang.split('-')[0]
        if not isinstance(self.features, dict):
            return []
        if lang not in self.features:
            lang = 'ru'
        return self.features.get(lang, [])

    def get_development_time(self, lang=None):
        if lang is None:
            from django.utils.translation import get_language
            lang = get_language() or 'ru'
        lang = lang.split('-')[0]
        if lang == 'en' and self.development_time_en:
            return self.development_time_en
        return self.development_time


# ============================================================
# FAQ
# ============================================================

class FAQSection(BaseModel):
    title = models.CharField(max_length=200, verbose_name=_("Section Title"))
    subtitle = models.CharField(max_length=300, blank=True, default='', verbose_name=_("Subtitle"))
    description = models.TextField(blank=True, default='', verbose_name=_("Description"))

    class Meta:
        verbose_name = _("FAQ Section")
        verbose_name_plural = _("FAQ Sections")

    def __str__(self):
        return self.title


class FAQItem(BaseModel):
    section = models.ForeignKey(
        FAQSection, on_delete=models.CASCADE,
        related_name='faqs', verbose_name=_("FAQ Section")
    )
    question = models.CharField(max_length=300, verbose_name=_("Question"))
    answer = models.TextField(verbose_name=_("Answer"))
    category = models.CharField(max_length=100, blank=True, default='', verbose_name=_("Category"))

    class Meta:
        verbose_name = _("FAQ Item")
        verbose_name_plural = _("FAQ Items")
        ordering = ['order']

    def __str__(self):
        return self.question[:50]


# ============================================================
# CTA
# ============================================================

class CTASection(BaseModel):
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    badge = models.CharField(max_length=50, blank=True, default='', verbose_name=_("Badge"))
    description = models.TextField(blank=True, default='', verbose_name=_("Description"))

    image_light = models.ImageField(
        upload_to='cta/light/', blank=True, null=True, verbose_name=_("Image Light Theme")
    )
    image_dark = models.ImageField(
        upload_to='cta/dark/', blank=True, null=True, verbose_name=_("Image Dark Theme")
    )

    image_light_thumbnail = ImageSpecField(
        source='image_light', processors=[ResizeToFill(800, 500)],
        format='WEBP', options={'quality': 85}
    )
    image_dark_thumbnail = ImageSpecField(
        source='image_dark', processors=[ResizeToFill(800, 500)],
        format='WEBP', options={'quality': 85}
    )

    button_text = models.CharField(max_length=50, default=_("Submit request"), verbose_name=_("Button text"))
    button_url = models.CharField(max_length=200, default="/contacts/", verbose_name=_("Button URL"))
    note = models.CharField(max_length=100, blank=True, default='', verbose_name=_("Note"))

    class Meta:
        verbose_name = _("CTA Section")
        verbose_name_plural = _("CTA Sections")

    def __str__(self):
        return self.title

    def get_image_for_theme(self, theme='light'):
        if theme == 'dark' and self.image_dark:
            return self.image_dark_thumbnail or self.image_dark
        return self.image_light_thumbnail or self.image_light

    @staticmethod
    def _get_lang(lang):
        if lang is None:
            from django.utils.translation import get_language
            lang = get_language() or 'ru'
        return lang.split('-')[0]

    def get_badge(self, lang=None):
        lang = self._get_lang(lang)
        if hasattr(self, 'badge_ru'):
            return getattr(self, f'badge_{lang}', self.badge_ru)
        return self.badge

    def get_title(self, lang=None):
        lang = self._get_lang(lang)
        if hasattr(self, 'title_ru'):
            return getattr(self, f'title_{lang}', self.title_ru)
        return self.title

    def get_description(self, lang=None):
        lang = self._get_lang(lang)
        if hasattr(self, 'description_ru'):
            return getattr(self, f'description_{lang}', self.description_ru)
        return self.description

    def get_button_text(self, lang=None):
        lang = self._get_lang(lang)
        if hasattr(self, 'button_text_ru'):
            return getattr(self, f'button_text_{lang}', self.button_text_ru)
        return self.button_text

    def get_note(self, lang=None):
        lang = self._get_lang(lang)
        if hasattr(self, 'note_ru'):
            return getattr(self, f'note_{lang}', self.note_ru)
        return self.note


# ============================================================
# REVIEWS
# ============================================================

class ReviewsSection(BaseModel):
    title = models.CharField(max_length=200, verbose_name=_("Section Title"))
    subtitle = models.CharField(max_length=300, blank=True, default='', verbose_name=_("Subtitle"))
    description = models.TextField(blank=True, default='', verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Reviews Section")
        verbose_name_plural = _("Reviews Sections")

    def __str__(self):
        return self.title


class Review(BaseModel):
    section = models.ForeignKey(
        ReviewsSection, on_delete=models.CASCADE,
        related_name='reviews', verbose_name=_("Reviews Section")
    )
    client_name = models.CharField(max_length=100, verbose_name=_("Client name"))
    client_position = models.CharField(max_length=100, blank=True, default='', verbose_name=_("Position"))
    client_company = models.CharField(max_length=100, blank=True, default='', verbose_name=_("Company"))

    client_photo_light = models.ImageField(
        upload_to='reviews/light/', blank=True, null=True, verbose_name=_("Client photo Light Theme")
    )
    client_photo_dark = models.ImageField(
        upload_to='reviews/dark/', blank=True, null=True, verbose_name=_("Client photo Dark Theme")
    )

    client_photo_light_thumbnail = ImageSpecField(
        source='client_photo_light', processors=[ResizeToFill(100, 100)],
        format='WEBP', options={'quality': 85}
    )
    client_photo_dark_thumbnail = ImageSpecField(
        source='client_photo_dark', processors=[ResizeToFill(100, 100)],
        format='WEBP', options={'quality': 85}
    )

    content = models.TextField(verbose_name=_("Review text"))
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5, verbose_name=_("Rating")
    )
    project_url = models.URLField(blank=True, default='', verbose_name=_("Project URL"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Featured"))

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.client_name} - {self.rating}★"

    def get_photo_for_theme(self, theme='light'):
        if theme == 'dark' and self.client_photo_dark:
            return self.client_photo_dark_thumbnail or self.client_photo_dark
        return self.client_photo_light_thumbnail or self.client_photo_light


# ============================================================
# CONTACT PAGE
# ============================================================

class ContactPage(models.Model):
    """Страница контактов"""
    title = models.CharField(max_length=200, default=_("Contacts"), verbose_name=_("Page Title"))

    phone = models.CharField(max_length=50, verbose_name=_("Phone"))
    email = models.EmailField(verbose_name=_("Email"))
    address = models.CharField(max_length=200, verbose_name=_("Address"))

    telegram = models.URLField(blank=True, default='', verbose_name=_("Telegram"))
    max_messenger = models.URLField(blank=True, default='', verbose_name=_("MAX"))
    whatsapp = models.URLField(blank=True, default='', verbose_name=_("WhatsApp"))
    linkedin = models.URLField(blank=True, default='', verbose_name=_("LinkedIn"))
    pinterest = models.URLField(blank=True, default='', verbose_name=_("Pinterest"))
    instagram = models.URLField(blank=True, default='', verbose_name=_("Instagram"))
    youtube = models.URLField(blank=True, default='', verbose_name=_("YouTube"))
    github = models.URLField(blank=True, default='', verbose_name=_("GitHub"))

    # ============================================================
    # ABOUT SECTION (переиспользуем существующие поля)
    # ============================================================

    about_label = models.CharField(
        max_length=100, blank=True, default='О КОМПАНИИ',
        verbose_name=_("About Label"),
        help_text=_("Маленькая надпись над заголовком (RU)"),
    )
    about_label_en = models.CharField(
        max_length=100, blank=True, default='ABOUT US',
        verbose_name=_("About Label (EN)"),
        help_text=_("Маленькая надпись над заголовком (EN)"),
    )

    about_title = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name=_("About Title")
    )
    about_subtitle = models.CharField(
        max_length=300, blank=True, default='',
        verbose_name=_("About Subtitle"),
        help_text=_("Краткое описание под заголовком"),
    )

    about_text = RichTextField(
        blank=True, default='',
        verbose_name=_("About Text"),
        config_name='basic'
    )

    # Существующее поле — оставляем как fallback
    about_image = models.ImageField(
        upload_to='contact/about/', blank=True, null=True,
        verbose_name=_("About Image (fallback)")
    )

    # 4 картинки для разных комбинаций темы/языка
    about_image_light_ru = models.ImageField(
        upload_to='contact/about/light/ru/', blank=True, null=True,
        verbose_name=_("About Image Light + RU")
    )
    about_image_light_en = models.ImageField(
        upload_to='contact/about/light/en/', blank=True, null=True,
        verbose_name=_("About Image Light + EN")
    )
    about_image_dark_ru = models.ImageField(
        upload_to='contact/about/dark/ru/', blank=True, null=True,
        verbose_name=_("About Image Dark + RU")
    )
    about_image_dark_en = models.ImageField(
        upload_to='contact/about/dark/en/', blank=True, null=True,
        verbose_name=_("About Image Dark + EN")
    )

    # Миниатюры для 4 картинок
    about_image_light_ru_thumbnail = ImageSpecField(
        source='about_image_light_ru',
        processors=[ResizeToFill(1200, 900)],
        format='WEBP', options={'quality': 85}
    )
    about_image_light_en_thumbnail = ImageSpecField(
        source='about_image_light_en',
        processors=[ResizeToFill(1200, 900)],
        format='WEBP', options={'quality': 85}
    )
    about_image_dark_ru_thumbnail = ImageSpecField(
        source='about_image_dark_ru',
        processors=[ResizeToFill(1200, 900)],
        format='WEBP', options={'quality': 85}
    )
    about_image_dark_en_thumbnail = ImageSpecField(
        source='about_image_dark_en',
        processors=[ResizeToFill(1200, 900)],
        format='WEBP', options={'quality': 85}
    )

    # Миниатюра для старого fallback-поля
    about_image_thumbnail = ImageSpecField(
        source='about_image',
        processors=[ResizeToFill(1200, 900)],
        format='WEBP', options={'quality': 85}
    )

    class Meta:
        verbose_name = _("Contact Page")
        verbose_name_plural = _("Contact Page")

    def __str__(self):
        return self.title

    # ============================================================
    # ХЕЛПЕРЫ ДЛЯ ABOUT SECTION
    # ============================================================

    @staticmethod
    def _get_lang(lang):
        if lang is None:
            from django.utils.translation import get_language
            lang = get_language() or 'ru'
        return lang.split('-')[0]

    def get_about_label(self, lang=None):
        lang = self._get_lang(lang)
        if lang == 'en' and self.about_label_en:
            return self.about_label_en
        return self.about_label or 'О КОМПАНИИ'

    def get_about_image(self, theme='light', language='ru'):
        """Fallback-логика: dark→light, en→ru, потом старое about_image."""
        field_name = f"about_image_{theme}_{language}"
        image = getattr(self, field_name, None)
        if image:
            return image

        if theme == 'dark' and language == 'en':
            return (
                self.about_image_dark_ru
                or self.about_image_light_en
                or self.about_image_light_ru
                or self.about_image
            )
        elif theme == 'dark':
            return self.about_image_dark_ru or self.about_image_light_ru or self.about_image
        elif language == 'en':
            return self.about_image_light_en or self.about_image_light_ru or self.about_image
        return self.about_image_light_ru or self.about_image

    def get_about_image_url(self, theme='light', language='ru'):
        img = self.get_about_image(theme, language)
        return img.url if img else None


# ============================================================
# BLOG
# ============================================================

class BlogCategory(BaseModel):
    """Категория блога"""
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    slug = models.SlugField(unique=True, blank=True, verbose_name=_("URL slug"))
    description = models.TextField(blank=True, default='', verbose_name=_("Description"))
    icon = models.CharField(
        max_length=50, blank=True, default='',
        verbose_name=_("Icon"),
        help_text=_('Font Awesome icon class, e.g. "fa-code", "fa-python", "fa-database"')
    )

    icon_png = models.ImageField(
        upload_to='blog/categories/icons/', blank=True, null=True,
        verbose_name=_("Icon PNG"),
        help_text=_('Загрузите PNG иконку для категории (рекомендуемый размер: 64x64px)')
    )
    icon_png_thumbnail = ImageSpecField(
        source='icon_png', processors=[ResizeToFit(64, 64)],
        format='PNG', options={'quality': 90}
    )

    # SEO (ручной ввод RU/EN)
    seo_title_ru = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name=_("SEO Title (RU)"),
        help_text=_("Если пусто — используется SEO раздела «Блог»")
    )
    seo_title_en = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name=_("SEO Title (EN)"),
        help_text=_("Если пусто — используется SEO раздела «Блог»")
    )
    seo_description_ru = models.CharField(
        max_length=500, blank=True, default='',
        verbose_name=_("SEO Description (RU)"),
        help_text=_("Если пусто — используется SEO раздела «Блог»")
    )
    seo_description_en = models.CharField(
        max_length=500, blank=True, default='',
        verbose_name=_("SEO Description (EN)"),
        help_text=_("Если пусто — используется SEO раздела «Блог»")
    )

    class Meta:
        verbose_name = _("Blog Category")
        verbose_name_plural = _("Blog Categories")
        ordering = ['order']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_icon_html(self):
        if self.icon_png:
            return (
                f'<img src="{self.icon_png.url}" alt="{self.name}" '
                f'style="width:24px;height:24px;object-fit:contain;">'
            )
        elif self.icon:
            return f'<i class="fas {self.icon}"></i>'
        return ''

    @staticmethod
    def _get_lang(lang):
        if lang is None:
            from django.utils.translation import get_language
            lang = get_language() or 'ru'
        return lang.split('-')[0]

    def get_seo_title(self, lang=None):
        lang = self._get_lang(lang)
        value = getattr(self, f'seo_title_{lang}', '') or ''
        if value.strip():
            return value.strip()
        if lang != 'ru':
            value_ru = self.seo_title_ru or ''
            if value_ru.strip():
                return value_ru.strip()
        return ''

    def get_seo_description(self, lang=None):
        lang = self._get_lang(lang)
        value = getattr(self, f'seo_description_{lang}', '') or ''
        if value.strip():
            return value.strip()
        if lang != 'ru':
            value_ru = self.seo_description_ru or ''
            if value_ru.strip():
                return value_ru.strip()
        return ''


class BlogPost(BaseModel):
    """Пост блога"""
    category = models.ForeignKey(
        BlogCategory, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='posts', verbose_name=_("Category")
    )
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    slug = models.SlugField(unique=True, blank=True, verbose_name=_("URL slug"))

    image_light = models.ImageField(
        upload_to='blog/light/', blank=True, null=True, verbose_name=_("Image Light Theme")
    )
    image_dark = models.ImageField(
        upload_to='blog/dark/', blank=True, null=True, verbose_name=_("Image Dark Theme")
    )

    image_light_thumbnail = ImageSpecField(
        source='image_light', processors=[ResizeToFill(1200, 630)],
        format='WEBP', options={'quality': 85}
    )
    image_dark_thumbnail = ImageSpecField(
        source='image_dark', processors=[ResizeToFill(1200, 630)],
        format='WEBP', options={'quality': 85}
    )

    excerpt = RichTextField(
        verbose_name=_("Excerpt"),
        help_text=_("Краткое описание поста, отображается в списке блога"),
        config_name='basic'
    )
    content = RichTextField(
        verbose_name=_("Content"),
        help_text=_("Полное содержание поста"),
        config_name='default'
    )

    author = models.CharField(max_length=100, default='LYNXREACTOR', verbose_name=_("Author"))

    pdf_file = models.FileField(
        upload_to='blog/pdfs/', blank=True, null=True,
        verbose_name=_("PDF File"),
        help_text=_('Загрузите PDF файл для скачивания (опционально)'),
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf']),
            validate_pdf_file,
        ],
    )

    likes = models.PositiveIntegerField(default=0, verbose_name=_("Likes"), help_text=_("Number of likes"))
    dislikes = models.PositiveIntegerField(default=0, verbose_name=_("Dislikes"), help_text=_("Number of dislikes"))

    published_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Published at"))
    is_published = models.BooleanField(default=False, verbose_name=_("Published"))

    tags = models.JSONField(default=list, blank=True, validators=[validate_tags], verbose_name=_("Tags"), help_text=_('["tag1", "tag2"]'))

    views = models.PositiveIntegerField(
        default=0, verbose_name=_("Views count"),
        help_text=_("Number of times this post has been viewed")
    )

    # SEO (ручной ввод RU/EN)
    seo_title_ru = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name=_("SEO Title (RU)"),
        help_text=_("Если пусто — используется SEO раздела «Блог»")
    )
    seo_title_en = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name=_("SEO Title (EN)"),
        help_text=_("Если пусто — используется SEO раздела «Блог»")
    )
    seo_description_ru = models.CharField(
        max_length=500, blank=True, default='',
        verbose_name=_("SEO Description (RU)"),
        help_text=_("Если пусто — используется SEO раздела «Блог»")
    )
    seo_description_en = models.CharField(
        max_length=500, blank=True, default='',
        verbose_name=_("SEO Description (EN)"),
        help_text=_("Если пусто — используется SEO раздела «Блог»")
    )

    class Meta:
        verbose_name = _("Blog Post")
        verbose_name_plural = _("Blog Posts")
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['-published_at'], name='blog_pub_desc_idx'),
            models.Index(fields=['-views'], name='blog_views_desc_idx'),
            models.Index(fields=['is_published', 'is_active', '-published_at'],
                         name='blog_pub_active_idx'),
            models.Index(fields=['category', '-published_at'],
                         name='blog_cat_pub_idx'),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('agency:blog_detail', kwargs={'slug': self.slug})

    def get_image_for_theme(self, theme='light'):
        if theme == 'dark' and self.image_dark:
            return self.image_dark_thumbnail or self.image_dark
        return self.image_light_thumbnail or self.image_light

    def increment_views(self):
        """
        Увеличивает счётчик просмотров через UPDATE.
        Не триггерит post_save signals → не инвалидирует кеш на каждый просмотр.
        """
        from django.db.models import F
        BlogPost.objects.filter(pk=self.pk).update(views=F('views') + 1)
        self.views += 1  # для консистентности в текущем объекте

    @property
    def rating(self):
        return self.likes - self.dislikes

    @property
    def total_votes(self):
        return self.likes + self.dislikes

    @property
    def reading_time(self):
        """
        Приблизительное время чтения в минутах.
        Средняя скорость: 200 слов/мин (консервативно для IT-контента).
        Минимум — 1 минута.
        """
        import re
        from django.utils.html import strip_tags

        if not self.content:
            return 1

        # Убираем HTML-теги и считаем слова
        text = strip_tags(self.content)
        # Убираем код-блоки? Нет — код тоже читают. Оставляем.
        words = len(re.findall(r'\w+', text))

        minutes = max(1, round(words / 200))
        return minutes

    @staticmethod
    def _get_lang(lang):
        if lang is None:
            from django.utils.translation import get_language
            lang = get_language() or 'ru'
        return lang.split('-')[0]

    def get_seo_title(self, lang=None):
        lang = self._get_lang(lang)
        value = getattr(self, f'seo_title_{lang}', '') or ''
        if value.strip():
            return value.strip()
        if lang != 'ru':
            value_ru = self.seo_title_ru or ''
            if value_ru.strip():
                return value_ru.strip()
        return ''

    def get_seo_description(self, lang=None):
        lang = self._get_lang(lang)
        value = getattr(self, f'seo_description_{lang}', '') or ''
        if value.strip():
            return value.strip()
        if lang != 'ru':
            value_ru = self.seo_description_ru or ''
            if value_ru.strip():
                return value_ru.strip()
        return ''


class BlogPostVote(models.Model):
    VOTE_CHOICES = [('like', _('Like')), ('dislike', _('Dislike'))]

    post = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE,
        related_name='votes', verbose_name=_("Post")
    )
    vote_type = models.CharField(max_length=10, choices=VOTE_CHOICES, verbose_name=_("Vote type"))
    ip_address = models.GenericIPAddressField(verbose_name=_("IP address"))
    user_agent = models.CharField(max_length=255, blank=True, default='', verbose_name=_("User Agent"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))

    class Meta:
        verbose_name = _("Blog Post Vote")
        verbose_name_plural = _("Blog Post Votes")
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['post', 'ip_address'],
                name='unique_post_ip_vote',
            ),
        ]
        indexes = [
            models.Index(fields=['post', 'ip_address'], name='vote_post_ip_idx'),
        ]

    def __str__(self):
        return f"{self.post.title} - {self.vote_type} ({self.ip_address})"


# ============================================================
# CONTACT REQUESTS
# ============================================================

class ContactRequest(models.Model):
    STATUS_CHOICES = [
        ('new', _('New')),
        ('in_progress', _('In progress')),
        ('completed', _('Completed')),
        ('rejected', _('Rejected')),
    ]
    CONTACT_METHOD_CHOICES = [
        ('phone', _('Phone')),
        ('telegram', _('Telegram')),
        ('whatsapp', _('WhatsApp')),
        ('viber', _('Viber')),
        ('email', _('Email')),
    ]

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    email = models.EmailField(verbose_name=_("Email"))
    phone = models.CharField(max_length=50, blank=True, verbose_name=_("Phone"))
    contact_method = models.CharField(
        max_length=20, choices=CONTACT_METHOD_CHOICES, blank=True,
        verbose_name=_("Contact method")
    )
    contact_value = models.CharField(max_length=200, blank=True, verbose_name=_("Contact details"))
    tariff = models.ForeignKey(
        'Tariff', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_("Tariff")
    )
    message = models.TextField(verbose_name=_("Message"))
    turnstile_verified = models.BooleanField(
        default=False,
        verbose_name=_("Turnstile verified"),
        help_text=_("Прошла ли заявка проверку Cloudflare Turnstile"),
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='new', verbose_name=_("Status")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Date created"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Date updated"))
    user_agent = models.TextField(blank=True, verbose_name=_("User Agent"))
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_("IP address"))
    referer = models.URLField(
        max_length=2048, blank=True,
        verbose_name=_("Referrer"),
    )

    language = models.CharField(
        max_length=5,
        default='ru',
        choices=[('ru', 'Русский'), ('en', 'English')],
        verbose_name=_("Language"),
        help_text=_("Язык, на котором клиент отправил заявку"),
    )

    class Meta:
        verbose_name = _("Contact Request")
        verbose_name_plural = _("Contact Requests")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at'], name='contact_created_idx'),
            models.Index(fields=['status', '-created_at'], name='contact_status_idx'),
        ]

    def __str__(self):
        return f"{self.name} - {self.email}"


# ============================================================
# SITE CONFIGURATION
# ============================================================

class SiteConfiguration(models.Model):
    site_name = models.CharField(max_length=100, default="LYNXREACTOR", verbose_name=_("Site name"))
    site_description = models.TextField(
        max_length=500,
        default=_("The Engine of Web Evolution — premium Python/Django web development"),
        verbose_name=_("Site description")
    )

    logo_light = models.ImageField(
        upload_to='site/light/', blank=True, null=True, verbose_name=_("Logo Light Theme")
    )
    logo_dark = models.ImageField(
        upload_to='site/dark/', blank=True, null=True, verbose_name=_("Logo Dark Theme")
    )

    favicon = models.ImageField(
        upload_to='site/', blank=True, null=True, verbose_name=_("Favicon")
    )
    favicon_thumbnail = ImageSpecField(
        source='favicon', processors=[ResizeToFit(64, 64)],
        format='PNG', options={'quality': 90}
    )

    og_image = models.ImageField(
        upload_to='site/', blank=True, null=True,
        verbose_name=_("OG Image"),
        help_text=_("Global Open Graph image (1200x630 recommended)")
    )
    og_image_thumbnail = ImageSpecField(
        source='og_image', processors=[ResizeToFill(1200, 630)],
        format='WEBP', options={'quality': 85}
    )

    default_seo_title = models.CharField(
        max_length=200, blank=True, default='', verbose_name=_("Default SEO Title")
    )
    default_seo_description = models.CharField(
        max_length=500, blank=True, default='', verbose_name=_("Default SEO Description")
    )

    is_maintenance_mode = models.BooleanField(default=False, verbose_name=_("Maintenance mode"))
    maintenance_text = models.TextField(blank=True, default='', verbose_name=_("Maintenance text"))

    class Meta:
        verbose_name = _("Site Configuration")
        verbose_name_plural = _("Site Configuration")

    def __str__(self):
        return self.site_name

    def get_logo_for_theme(self, theme='light'):
        if theme == 'dark' and self.logo_dark:
            return self.logo_dark
        return self.logo_light


# ============================================================
# TELEGRAM LOGS
# ============================================================

class TelegramLog(models.Model):
    LOG_TYPES = [
        ('contact', 'Contact Form'),
        ('error', 'Error'),
        ('status', 'Server Status'),
        ('debug', 'Debug'),
        ('info', 'Info'),
    ]

    log_type = models.CharField(
        max_length=20, choices=LOG_TYPES, default='info', verbose_name=_("Log Type")
    )
    chat_id = models.CharField(max_length=50, verbose_name=_("Chat ID"))
    message = models.TextField(verbose_name=_("Message"))
    is_sent = models.BooleanField(default=True, verbose_name=_("Is Sent"))
    error = models.TextField(blank=True, default='', verbose_name=_("Error"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Telegram Log")
        verbose_name_plural = _("Telegram Logs")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_log_type_display()} - {self.created_at}"


# ============================================================
# MISSION
# ============================================================

class Mission(BaseModel):
    PAGE_CHOICES = [
        ('home', _('Home')),
        ('contacts', _('Contacts')),
        ('blog', _('Blog')),
        ('blog_detail', _('Blog Detail (article page)')),
        ('portfolio', _('Portfolio')),  # зарезервировано
        ('about', _('About')),          # зарезервировано
    ]

    page = models.CharField(
        max_length=20, choices=PAGE_CHOICES, unique=True, verbose_name=_("Page")
    )
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    subtitle = models.CharField(max_length=300, blank=True, default='', verbose_name=_("Subtitle"))
    description = RichTextField(blank=True, default='', verbose_name=_("Description"), config_name='basic')

    background_light = models.ImageField(
        upload_to='mission/light/', blank=True, null=True, verbose_name=_("Background Light Theme")
    )
    background_dark = models.ImageField(
        upload_to='mission/dark/', blank=True, null=True, verbose_name=_("Background Dark Theme")
    )

    background_light_thumbnail = ImageSpecField(
        source='background_light', processors=[ResizeToFill(1920, 1080)],
        format='WEBP', options={'quality': 85}
    )
    background_dark_thumbnail = ImageSpecField(
        source='background_dark', processors=[ResizeToFill(1920, 1080)],
        format='WEBP', options={'quality': 85}
    )

    button_text = models.CharField(max_length=50, blank=True, default='', verbose_name=_("Button text"))
    button_url = models.CharField(max_length=200, blank=True, default='', verbose_name=_("Button URL"))

    class Meta:
        verbose_name = _("Mission")
        verbose_name_plural = _("Missions")

    def __str__(self):
        return f"{self.get_page_display()} — {self.title}"


# ============================================================
# PAGE SEO
# ============================================================

class PageSEO(models.Model):
    """
    SEO-настройки для каждой страницы сайта.
    Каждая страница имеет отдельную запись с уникальным page_key.
    SEO-тексты вводятся вручную для RU и EN (без автоматического перевода).
    Fallback — agency/seo_defaults.py.
    """

    PAGE_CHOICES = [
        ('home', _('Главная')),
        ('contact', _('Контакты')),
        ('blog', _('Блог')),

        # ============================================================
        # ЗАДЕЛ НА БУДУЩЕЕ — пока не используются как отдельные страницы
        # ============================================================
        # Эти ключи зарезервированы для случаев, когда появятся
        # отдельные URL (/portfolio/, /about/, /services/, /pricing/).
        # Сейчас соответствующий контент — секции на главной.
        # Чтобы активировать — создать вью с seo_page_key='portfolio' и т.п.
        # ============================================================
        ('portfolio', _('Портфолио (секция главной)')),
        ('about', _('О нас (секция на /contact/)')),
        ('services', _('Услуги (секция главной)')),
        ('pricing', _('Тарифы (секция главной)')),
    ]

    page_key = models.CharField(
        max_length=50, choices=PAGE_CHOICES, unique=True,
        verbose_name=_("Страница"),
        help_text=_("Уникальный идентификатор страницы")
    )

    # SEO RU
    title_ru = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name=_("SEO Title (RU)"),
        help_text=_("Рекомендуемая длина: 50–60 символов")
    )
    description_ru = models.TextField(
        max_length=500, blank=True, default='',
        verbose_name=_("SEO Description (RU)"),
        help_text=_("Рекомендуемая длина: 150–160 символов")
    )
    keywords_ru = models.TextField(
        blank=True, default='',
        verbose_name=_("SEO Keywords (RU)"),
        help_text=_("Ключевые слова через запятую. Ориентировано на Яндекс.")
    )

    # SEO EN
    title_en = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name=_("SEO Title (EN)"),
        help_text=_("Рекомендуемая длина: 50–60 символов")
    )
    description_en = models.TextField(
        max_length=500, blank=True, default='',
        verbose_name=_("SEO Description (EN)"),
        help_text=_("Рекомендуемая длина: 150–160 символов")
    )
    keywords_en = models.TextField(
        blank=True, default='',
        verbose_name=_("SEO Keywords (EN)"),
        help_text=_("Ключевые слова через запятую")
    )

    # Open Graph
    og_title_ru = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name=_("OG Title (RU)"),
        help_text=_("Если пусто — используется SEO Title")
    )
    og_title_en = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name=_("OG Title (EN)"),
        help_text=_("Если пусто — используется SEO Title")
    )
    og_description_ru = models.TextField(
        max_length=500, blank=True, default='',
        verbose_name=_("OG Description (RU)"),
        help_text=_("Если пусто — используется SEO Description")
    )
    og_description_en = models.TextField(
        max_length=500, blank=True, default='',
        verbose_name=_("OG Description (EN)"),
        help_text=_("Если пусто — используется SEO Description")
    )

    is_active = models.BooleanField(default=True, verbose_name=_("Активно"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    class Meta:
        verbose_name = _("SEO страницы")
        verbose_name_plural = _("SEO страницы")
        ordering = ['page_key']

    def __str__(self):
        return f"SEO: {self.get_page_key_display()}"

    @staticmethod
    def _normalize_lang(lang):
        if lang is None:
            from django.utils.translation import get_language
            lang = get_language() or 'ru'
        return (lang or 'ru').split('-')[0]

    def _get_field(self, field_base, lang):
        from .seo_defaults import get_default_seo
        lang = self._normalize_lang(lang)
        value = getattr(self, f'{field_base}_{lang}', '') or ''
        if value.strip():
            return value.strip()
        if lang != 'ru':
            value_ru = getattr(self, f'{field_base}_ru', '') or ''
            if value_ru.strip():
                return value_ru.strip()
        defaults = get_default_seo(self.page_key, lang)
        return defaults.get(field_base, '')

    def get_title(self, lang=None):
        return self._get_field('title', lang)

    def get_description(self, lang=None):
        return self._get_field('description', lang)

    def get_keywords(self, lang=None):
        return self._get_field('keywords', lang)

    def get_og_title(self, lang=None):
        lang = self._normalize_lang(lang)
        value = getattr(self, f'og_title_{lang}', '') or ''
        if value.strip():
            return value.strip()
        if lang != 'ru':
            value_ru = getattr(self, 'og_title_ru', '') or ''
            if value_ru.strip():
                return value_ru.strip()
        return self.get_title(lang)

    def get_og_description(self, lang=None):
        lang = self._normalize_lang(lang)
        value = getattr(self, f'og_description_{lang}', '') or ''
        if value.strip():
            return value.strip()
        if lang != 'ru':
            value_ru = getattr(self, 'og_description_ru', '') or ''
            if value_ru.strip():
                return value_ru.strip()
        return self.get_description(lang)

    def has_custom_title(self, lang=None):
        lang = self._normalize_lang(lang)
        return bool((getattr(self, f'title_{lang}', '') or '').strip())

    @classmethod
    def get_for_page(cls, page_key, lang=None):
        try:
            return cls.objects.get(page_key=page_key, is_active=True)
        except cls.DoesNotExist:
            return cls(page_key=page_key)
        except cls.MultipleObjectsReturned:
            return cls.objects.filter(page_key=page_key, is_active=True).first()


    # ============================================================
    # SUBSCRIBERS (подписка на обновления блога)
    # ============================================================


class Subscriber(models.Model):
    """
    Подписчик на обновления блога.

    Хранит email, флаг активности, IP, источник подписки,
    unsubscribe-токен и служебные поля для рассылки.
    """
    email = models.EmailField(unique=True, verbose_name=_("Email"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    source = models.CharField(
        max_length=50, blank=True, default='blog_detail',
        verbose_name=_("Source"),
        help_text=_("Откуда пришла подписка (blog_detail, blog_list_sidebar, footer)"),
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_("IP address"))
    user_agent = models.CharField(max_length=255, blank=True, default='', verbose_name=_("User Agent"))

    # Токен для отписки (ссылка в письмах)
    unsubscribe_token = models.CharField(
        max_length=64, unique=True, blank=True, default='',
        verbose_name=_("Unsubscribe token"),
        help_text=_("Используется в ссылке для отписки"),
    )

    # Служебные поля рассылки
    last_emailed_at = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Last emailed at"),
        help_text=_("Когда последний раз отправляли рассылку"),
    )
    unsubscribed_at = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Unsubscribed at"),
        help_text=_("Когда подписчик отписался"),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Date created"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Date updated"))

    class Meta:
        verbose_name = _("Subscriber")
        verbose_name_plural = _("Subscribers")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at'], name='subscriber_created_idx'),
            models.Index(fields=['is_active'], name='subscriber_active_idx'),
            models.Index(fields=['unsubscribe_token'], name='subscriber_token_idx'),
        ]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Генерируем unsubscribe-токен при первом сохранении
        if not self.unsubscribe_token:
            import secrets
            self.unsubscribe_token = secrets.token_urlsafe(32)[:64]
        super().save(*args, **kwargs)

    def unsubscribe(self):
        """Отписать и зафиксировать дату."""
        from django.utils import timezone
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save(update_fields=['is_active', 'unsubscribed_at', 'updated_at'])

    def get_unsubscribe_url(self):
        """Полный URL для отписки (используется в письмах)."""
        from django.conf import settings
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        return f"{site_url}/unsubscribe/?token={self.unsubscribe_token}"