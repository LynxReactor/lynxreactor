# agency/admin.py

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin

from .models import (
    HeroSection,
    ServicesSection, ServiceItem,
    TechSection, TechItem,
    LandingSection, LandingFeature, LandingDetail,
    BusinessSection, BusinessFeature, BusinessDetail,
    RefactorSection, RefactorFeature, RefactorDetail,
    PortfolioSection, PortfolioItem,
    Tariff,
    FAQSection, FAQItem,
    CTASection,
    ReviewsSection, Review,
    ContactPage,
    BlogCategory, BlogPost,
    ContactRequest,
    SiteConfiguration,
    TelegramLog,
    Mission,
    PageSEO,
    Subscriber,
)
from .seo_defaults import get_default_seo

from .admin_actions import (
    export_selected_as_csv,
    export_selected_as_json,
    duplicate_selected,
    set_active_true,
    set_active_false,
    send_test_email,
    send_to_telegram,
    mark_as_new,
    mark_as_in_progress,
    mark_as_completed,
    mark_as_rejected,
    publish_selected,
    unpublish_selected,
    send_newsletter,
)

# ============================================================
# БАЗОВЫЕ АДМИН-КЛАССЫ
# ============================================================

class BaseAdmin(admin.ModelAdmin):
    """Базовый админ с общими настройками"""
    list_per_page = 25
    save_on_top = True


class BaseTranslationAdmin(TranslationAdmin, BaseAdmin):
    """Базовый админ с переводами"""
    pass


# ============================================================
# 1. HERO SECTION
# ============================================================

@admin.register(HeroSection)
class HeroSectionAdmin(BaseTranslationAdmin):
    list_display = ['page', 'title', 'is_active', 'preview_image']
    list_filter = ['page', 'is_active']
    search_fields = ['title', 'subtitle', 'description']
    list_editable = ['is_active']

    fieldsets = (
        ('Страница', {'fields': ('page',)}),
        ('Заголовки', {'fields': ('title', 'subtitle', 'description')}),
        ('Изображения', {
            'fields': (
                'hero_image_light_ru',
                'hero_image_light_en',
                'hero_image_dark_ru',
                'hero_image_dark_en',
            ),
            'description': _('Загрузите изображения для разных комбинаций темы и языка'),
            'classes': ('wide',),
        }),
        ('Кнопки', {
            'fields': ('cta_text', 'cta_url', 'secondary_cta_text', 'secondary_cta_url'),
            'classes': ('collapse',),
        }),
        ('Статус', {'fields': ('is_active',)}),
    )

    @admin.display(description=_('Preview'))
    def preview_image(self, obj):
        if obj.hero_image_light_ru:
            url = (
                obj.hero_image_light_ru_thumbnail.url
                if obj.hero_image_light_ru_thumbnail
                else obj.hero_image_light_ru.url
            )
            return format_html(
                '<img src="{}" width="100" height="56" '
                'style="object-fit:cover;border-radius:4px;" />',
                url
            )
        return _('No image')


# ============================================================
# 2. SERVICES SECTION
# ============================================================

class ServiceItemInline(admin.TabularInline):
    model = ServiceItem
    extra = 1
    fields = ['number', 'title', 'icon', 'image_light_ru', 'image_dark_ru', 'is_active', 'order']
    ordering = ['order', 'number']
    show_change_link = True


@admin.register(ServicesSection)
class ServicesSectionAdmin(BaseTranslationAdmin):
    list_display = ['title', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['title', 'subtitle', 'description']
    inlines = [ServiceItemInline]

    fieldsets = (
        ('Заголовки', {'fields': ('title', 'subtitle', 'description')}),
        ('Статус', {'fields': ('is_active', 'order')}),
    )


@admin.register(ServiceItem)
class ServiceItemAdmin(BaseTranslationAdmin):
    list_display = ['number', 'title', 'section', 'is_active', 'order']
    list_filter = ['section', 'is_active']
    search_fields = ['title', 'description']

    fieldsets = (
        ('Основное', {'fields': ('section', 'number', 'title', 'description', 'icon', 'url')}),
        ('Изображения', {
            'fields': (
                'image_light_ru', 'image_light_en',
                'image_dark_ru', 'image_dark_en',
            ),
            'description': _('Загрузите изображения для разных комбинаций темы и языка'),
        }),
        ('Статус', {'fields': ('order', 'is_active')}),
    )


# ============================================================
# 3. TECH SECTION
# ============================================================

class TechItemInline(admin.TabularInline):
    model = TechItem
    extra = 0
    fields = ['name', 'category', 'is_primary', 'logo', 'is_active', 'order']
    ordering = ['order']
    min_num = 0
    max_num = 20
    can_delete = True
    show_change_link = True
    verbose_name = _('Технология')
    verbose_name_plural = _('Технологии')


@admin.register(TechSection)
class TechSectionAdmin(BaseTranslationAdmin):
    list_display = ['title', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['title', 'subtitle', 'description']
    inlines = [TechItemInline]

    fieldsets = (
        ('Заголовки', {'fields': ('title', 'subtitle', 'description')}),
        ('Статус', {'fields': ('is_active', 'order')}),
    )


@admin.register(TechItem)
class TechItemAdmin(BaseTranslationAdmin):
    list_display = ['name', 'category', 'is_primary', 'is_active', 'order']
    list_filter = ['category', 'is_primary', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_primary', 'is_active', 'order']

    fieldsets = (
        ('Основное', {'fields': ('section', 'name', 'category', 'is_primary', 'description', 'url')}),
        ('Логотип', {'fields': ('logo',)}),
        ('Статус', {'fields': ('order', 'is_active')}),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field in ('logo', 'name', 'category'):
            if field in form.base_fields:
                form.base_fields[field].required = False
        return form


# ============================================================
# 4. LANDING SECTION
# ============================================================

class LandingFeatureInline(admin.TabularInline):
    model = LandingFeature
    extra = 1
    fields = ['icon', 'title_ru', 'title_en', 'description_ru', 'description_en', 'order']
    ordering = ['order']


class LandingDetailInline(admin.TabularInline):
    model = LandingDetail
    extra = 1
    fields = ['icon', 'title_ru', 'title_en', 'description_ru', 'description_en', 'order']
    ordering = ['order']


@admin.register(LandingSection)
class LandingSectionAdmin(admin.ModelAdmin):
    list_display = ['title_ru', 'title_en', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['title_ru', 'title_en', 'description_ru', 'description_en']
    list_editable = ['is_active', 'order']
    inlines = [LandingFeatureInline, LandingDetailInline]

    fieldsets = (
        ('Заголовки (RU)', {'fields': ('label_ru', 'title_ru', 'description_ru')}),
        ('Заголовки (EN)', {'fields': ('label_en', 'title_en', 'description_en')}),
        ('Изображения', {
            'fields': (
                'image_light_ru', 'image_light_en',
                'image_dark_ru', 'image_dark_en',
            ),
            'description': _('Загрузите изображения для разных комбинаций темы и языка'),
        }),
        ('Кнопка', {'fields': ('cta_text_ru', 'cta_text_en', 'cta_url')}),
        ('Статус', {'fields': ('is_active', 'order')}),
    )


@admin.register(LandingFeature)
class LandingFeatureAdmin(admin.ModelAdmin):
    list_display = ['title_ru', 'title_en', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['title_ru', 'title_en', 'description_ru', 'description_en']
    list_editable = ['is_active', 'order']


@admin.register(LandingDetail)
class LandingDetailAdmin(admin.ModelAdmin):
    list_display = ['title_ru', 'title_en', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['title_ru', 'title_en', 'description_ru', 'description_en']
    list_editable = ['is_active', 'order']


# ============================================================
# 5. BUSINESS SECTION
# ============================================================

class BusinessFeatureInline(admin.TabularInline):
    model = BusinessFeature
    extra = 1
    fields = ['icon', 'title_ru', 'title_en', 'description_ru', 'description_en', 'order']
    ordering = ['order']


class BusinessDetailInline(admin.TabularInline):
    model = BusinessDetail
    extra = 1
    fields = ['icon', 'title_ru', 'title_en', 'description_ru', 'description_en', 'order']
    ordering = ['order']


@admin.register(BusinessSection)
class BusinessSectionAdmin(admin.ModelAdmin):
    list_display = ['title_ru', 'title_en', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['title_ru', 'title_en', 'description_ru', 'description_en']
    list_editable = ['is_active', 'order']
    inlines = [BusinessFeatureInline, BusinessDetailInline]

    fieldsets = (
        ('Заголовки (RU)', {'fields': ('label_ru', 'title_ru', 'description_ru')}),
        ('Заголовки (EN)', {'fields': ('label_en', 'title_en', 'description_en')}),
        ('Изображения', {
            'fields': (
                'image_light_ru', 'image_light_en',
                'image_dark_ru', 'image_dark_en',
            ),
            'description': _('Загрузите изображения для разных комбинаций темы и языка'),
        }),
        ('Кнопка', {'fields': ('cta_text_ru', 'cta_text_en', 'cta_url')}),
        ('Статус', {'fields': ('is_active', 'order')}),
    )


@admin.register(BusinessFeature)
class BusinessFeatureAdmin(admin.ModelAdmin):
    list_display = ['title_ru', 'title_en', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['title_ru', 'title_en', 'description_ru', 'description_en']
    list_editable = ['is_active', 'order']


@admin.register(BusinessDetail)
class BusinessDetailAdmin(admin.ModelAdmin):
    list_display = ['title_ru', 'title_en', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['title_ru', 'title_en', 'description_ru', 'description_en']
    list_editable = ['is_active', 'order']


# ============================================================
# 6. REFACTOR SECTION
# ============================================================

class RefactorFeatureInline(admin.TabularInline):
    model = RefactorFeature
    extra = 1
    fields = ['icon', 'text_ru', 'text_en', 'order']
    ordering = ['order']


class RefactorDetailInline(admin.TabularInline):
    model = RefactorDetail
    extra = 1
    fields = ['icon', 'title_ru', 'title_en', 'description_ru', 'description_en', 'order']
    ordering = ['order']


@admin.register(RefactorSection)
class RefactorSectionAdmin(admin.ModelAdmin):
    list_display = ['title_ru', 'title_en', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['title_ru', 'title_en', 'description_ru', 'description_en']
    list_editable = ['is_active', 'order']
    inlines = [RefactorFeatureInline, RefactorDetailInline]

    fieldsets = (
        ('Заголовки (RU)', {'fields': ('label_ru', 'title_ru', 'description_ru')}),
        ('Заголовки (EN)', {'fields': ('label_en', 'title_en', 'description_en')}),
        ('Изображения', {
            'fields': (
                'image_light_ru', 'image_light_en',
                'image_dark_ru', 'image_dark_en',
            ),
            'description': _('Загрузите изображения для разных комбинаций темы и языка'),
        }),
        ('Кнопка', {'fields': ('cta_text_ru', 'cta_text_en', 'cta_url')}),
        ('Статус', {'fields': ('is_active', 'order')}),
    )


@admin.register(RefactorFeature)
class RefactorFeatureAdmin(admin.ModelAdmin):
    list_display = ['text_ru', 'text_en', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['text_ru', 'text_en']
    list_editable = ['is_active', 'order']


@admin.register(RefactorDetail)
class RefactorDetailAdmin(admin.ModelAdmin):
    list_display = ['title_ru', 'title_en', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['title_ru', 'title_en', 'description_ru', 'description_en']
    list_editable = ['is_active', 'order']


# ============================================================
# 7. PORTFOLIO SECTION
# ============================================================

class PortfolioItemInline(admin.TabularInline):
    model = PortfolioItem
    extra = 1
    fields = ['title_ru', 'title_en', 'category_ru', 'is_featured', 'is_active']
    ordering = ['-created_at']
    show_change_link = True


@admin.register(PortfolioSection)
class PortfolioSectionAdmin(admin.ModelAdmin):
    list_display = ['title_ru', 'title_en', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['title_ru', 'title_en', 'subtitle_ru', 'subtitle_en',
                     'description_ru', 'description_en']
    list_editable = ['is_active', 'order']
    inlines = [PortfolioItemInline]

    fieldsets = (
        ('Заголовки (RU)', {'fields': ('subtitle_ru', 'title_ru', 'description_ru')}),
        ('Заголовки (EN)', {'fields': ('subtitle_en', 'title_en', 'description_en')}),
        ('Статус', {'fields': ('is_active', 'order')}),
    )


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ['title_ru', 'title_en', 'category_ru', 'is_featured', 'is_active', 'preview_image']
    list_filter = ['is_featured', 'is_active', 'section']
    search_fields = ['title_ru', 'title_en', 'description_ru', 'description_en', 'client_name']
    prepopulated_fields = {'slug': ('title_ru',)}
    list_editable = ['is_featured', 'is_active']

    actions = [
        set_active_true,
        set_active_false,
        duplicate_selected,
        export_selected_as_csv,
        export_selected_as_json,
    ]

    fieldsets = (
        ('Основное', {
            'fields': ('section', 'title_ru', 'title_en', 'slug',
                       'category_ru', 'category_en', 'client_name')
        }),
        ('Контент', {
            'fields': ('description_ru', 'description_en', 'project_url', 'technologies')
        }),
        ('Изображения', {
            'fields': ('main_image_light', 'main_image_dark')
        }),
        # SEO с суффиксами _ru/_en
        ('SEO — Русский', {
            'fields': ('seo_title_ru', 'seo_description_ru'),
            'classes': ('collapse',),
            'description': _('Если пусто — используется SEO раздела «Портфолио»'),
        }),
        ('SEO — English', {
            'fields': ('seo_title_en', 'seo_description_en'),
            'classes': ('collapse',),
            'description': _('Если пусто — используется SEO раздела «Портфолио»'),
        }),
        ('Статус', {
            'fields': ('is_featured', 'order', 'is_active')
        }),
    )

    @admin.display(description=_('Preview'))
    def preview_image(self, obj):
        img = obj.main_image_light or obj.main_image_dark
        if img:
            return format_html(
                '<img src="{}" width="80" height="50" '
                'style="object-fit:cover;border-radius:4px;" />',
                img.url
            )
        return _('No image')


# ============================================================
# 8. TARIFFS
# ============================================================

@admin.register(Tariff)
class TariffAdmin(BaseTranslationAdmin):
    list_display = ['name', 'site_format', 'is_popular', 'is_custom', 'order', 'is_active']
    list_filter = ['is_popular', 'is_custom', 'is_active']
    search_fields = ['name', 'subtitle', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_popular', 'is_custom', 'is_active', 'order']

    actions = [
        set_active_true,
        set_active_false,
        export_selected_as_csv,
        export_selected_as_json,
    ]

    fieldsets = (
        ('Основное', {'fields': ('name', 'slug', 'site_format', 'subtitle', 'description')}),
        ('Время разработки', {'fields': ('development_time', 'development_time_en')}),
        ('Цены', {'fields': ('price_byn', 'price_rub', 'price_eur', 'price_usd')}),
        ('Особенности', {'fields': ('features',)}),
        ('Дизайн', {'fields': ('icon', 'accent_color')}),
        ('Статус', {'fields': ('is_popular', 'is_custom', 'order', 'is_active')}),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'features' in form.base_fields:
            form.base_fields['features'].help_text = (
                '{"ru": ["Особенность 1", "Особенность 2"], '
                '"en": ["Feature 1", "Feature 2"]}'
            )
        return form


# ============================================================
# 9. FAQ
# ============================================================

class FAQItemInline(admin.TabularInline):
    model = FAQItem
    extra = 1
    fields = ['question', 'category', 'order', 'is_active']
    ordering = ['order']


@admin.register(FAQSection)
class FAQSectionAdmin(BaseTranslationAdmin):
    list_display = ['title', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['title', 'subtitle', 'description']
    inlines = [FAQItemInline]

    fieldsets = (
        ('Заголовки', {'fields': ('title', 'subtitle', 'description')}),
        ('Статус', {'fields': ('is_active', 'order')}),
    )


@admin.register(FAQItem)
class FAQItemAdmin(BaseTranslationAdmin):
    list_display = ['question', 'category', 'order', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['question', 'answer']
    list_editable = ['is_active', 'order']


# ============================================================
# 10. CTA
# ============================================================

@admin.register(CTASection)
class CTASectionAdmin(BaseTranslationAdmin):
    list_display = ['title', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['title', 'description']

    fieldsets = (
        ('Заголовки', {'fields': ('title', 'badge', 'description')}),
        ('Изображения', {'fields': ('image_light', 'image_dark'), 'classes': ('collapse',)}),
        ('Кнопка', {'fields': ('button_text', 'button_url', 'note')}),
        ('Статус', {'fields': ('is_active', 'order')}),
    )


# ============================================================
# 11. REVIEWS
# ============================================================

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 1
    fields = ['client_name', 'rating', 'is_featured', 'is_active']
    ordering = ['-created_at']


@admin.register(ReviewsSection)
class ReviewsSectionAdmin(BaseTranslationAdmin):
    list_display = ['title', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['title', 'subtitle', 'description']
    inlines = [ReviewInline]

    fieldsets = (
        ('Заголовки', {'fields': ('title', 'subtitle', 'description')}),
        ('Статус', {'fields': ('is_active', 'order')}),
    )


@admin.register(Review)
class ReviewAdmin(BaseTranslationAdmin):
    list_display = ['client_name', 'client_company', 'rating', 'is_featured', 'is_active']
    list_filter = ['rating', 'is_featured', 'is_active']
    search_fields = ['client_name', 'client_company', 'content']
    list_editable = ['is_featured', 'is_active']

    fieldsets = (
        ('Клиент', {'fields': ('section', 'client_name', 'client_position', 'client_company')}),
        ('Фото', {'fields': ('client_photo_light', 'client_photo_dark'), 'classes': ('collapse',)}),
        ('Отзыв', {'fields': ('content', 'rating', 'project_url')}),
        ('Статус', {'fields': ('is_featured', 'order', 'is_active')}),
    )


# ============================================================
# 12. CONTACT PAGE
# ============================================================

@admin.register(ContactPage)
class ContactPageAdmin(TranslationAdmin):
    list_display = ['title', 'email', 'phone']
    search_fields = ['title', 'email', 'phone', 'address']

    fieldsets = (
        ('Основное', {'fields': ('title',)}),
        ('Контактная информация', {'fields': ('phone', 'email', 'address')}),
        ('Социальные сети', {
            'fields': ('telegram', 'whatsapp', 'max_messenger', 'linkedin', 'pinterest',
                       'instagram', 'youtube', 'github'),
            'classes': ('collapse',),
        }),
        ('О нас — Заголовки', {
            'fields': ('about_label', 'about_label_en', 'about_title', 'about_subtitle', 'about_text'),
            'description': _('Блок "О нас" отображается после Hero секции'),
        }),
        ('О нас — Изображения (Light)', {
            'fields': ('about_image_light_ru', 'about_image_light_en'),
            'classes': ('collapse',),
        }),
        ('О нас — Изображения (Dark)', {
            'fields': ('about_image_dark_ru', 'about_image_dark_en'),
            'classes': ('collapse',),
        }),
        ('О нас — Изображение (fallback)', {
            'fields': ('about_image',),
            'classes': ('collapse',),
            'description': _('Используется, если ни одно из 4 изображений выше не задано'),
        }),
    )

    def has_add_permission(self, request):
        return not ContactPage.objects.exists()


# ============================================================
# 13. BLOG
# ============================================================

@admin.register(BlogCategory)
class BlogCategoryAdmin(TranslationAdmin):
    """Админка категорий блога"""
    list_display = ['name', 'slug', 'is_active', 'order', 'preview_icon']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'order']

    actions = [
        set_active_true,
        set_active_false,
        duplicate_selected,
        export_selected_as_csv,
    ]


    fieldsets = (
        ('Основное', {'fields': ('name', 'slug', 'description')}),
        ('Иконка', {
            'fields': ('icon', 'icon_png'),
            'description': _('Выберите: Font Awesome иконку или загрузите PNG изображение'),
        }),
        #  SEO с суффиксами _ru/_en
        ('SEO — Русский', {
            'fields': ('seo_title_ru', 'seo_description_ru'),
            'classes': ('collapse',),
            'description': _('Если пусто — используется SEO раздела «Блог»'),
        }),
        ('SEO — English', {
            'fields': ('seo_title_en', 'seo_description_en'),
            'classes': ('collapse',),
            'description': _('Если пусто — используется SEO раздела «Блог»'),
        }),
        ('Статус', {'fields': ('is_active', 'order')}),
    )

    @admin.display(description=_('Icon'))
    def preview_icon(self, obj):
        if obj.icon_png:
            url = obj.icon_png_thumbnail.url if obj.icon_png_thumbnail else obj.icon_png.url
            return format_html(
                '<img src="{}" width="32" height="32" '
                'style="object-fit:contain;" />',
                url
            )
        if obj.icon:
            return format_html('<i class="fas {}" style="font-size:18px;"></i>', obj.icon)
        return '—'


@admin.register(BlogPost)
class BlogPostAdmin(TranslationAdmin):
    """Админка постов блога"""
    list_display = [
        'title', 'category', 'author', 'is_published', 'is_active',
        'views', 'likes', 'dislikes', 'published_at',
    ]
    list_filter = ['category', 'is_published', 'is_active', 'published_at']
    search_fields = ['title', 'excerpt', 'content', 'author']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published', 'is_active']
    date_hierarchy = 'published_at'
    readonly_fields = ['views', 'likes', 'dislikes']

    actions = [
        publish_selected,
        unpublish_selected,
        duplicate_selected,
        export_selected_as_csv,
        export_selected_as_json,
        send_newsletter,
    ]

    fieldsets = (
        ('Основное', {'fields': ('category', 'title', 'slug', 'author')}),
        ('Контент', {
            'fields': ('excerpt', 'content'),
            'description': _('Excerpt — краткое описание для списка блога. '
                             'Content — полный текст статьи.'),
        }),
        ('Изображения', {'fields': ('image_light', 'image_dark'), 'classes': ('collapse',)}),
        ('PDF материал', {'fields': ('pdf_file',), 'classes': ('collapse',)}),
        ('Публикация', {'fields': ('published_at', 'is_published')}),
        # SEO с суффиксами _ru/_en
        ('SEO — Русский', {
            'fields': ('seo_title_ru', 'seo_description_ru'),
            'classes': ('collapse',),
            'description': _('Если пусто — используется SEO раздела «Блог»'),
        }),
        ('SEO — English', {
            'fields': ('seo_title_en', 'seo_description_en'),
            'classes': ('collapse',),
            'description': _('Если пусто — используется SEO раздела «Блог»'),
        }),
        ('Статистика', {'fields': ('views', 'likes', 'dislikes'), 'classes': ('collapse',)}),
        ('Статус', {'fields': ('order', 'is_active')}),
    )

    class Media:
        css = {'all': ('admin/css/ckeditor-custom.css',)}

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field in ('excerpt', 'content'):
            if field in form.base_fields:
                form.base_fields[field].required = True
        return form


# ============================================================
# 14. CONTACT REQUESTS
# ============================================================

@admin.register(ContactRequest)
class ContactRequestAdmin(BaseAdmin):
    list_display = ['name', 'email', 'phone', 'contact_method', 'contact_value', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'contact_method']
    search_fields = ['name', 'email', 'phone', 'message']
    readonly_fields = ['created_at', 'updated_at', 'user_agent', 'ip_address', 'referer']
    list_editable = ['status']
    date_hierarchy = 'created_at'

    actions = [
        mark_as_new,
        mark_as_in_progress,
        mark_as_completed,
        mark_as_rejected,
        export_selected_as_csv,
        export_selected_as_json,
        send_test_email,
        send_to_telegram,
    ]

    fieldsets = (
        ('Клиент', {'fields': ('name', 'email', 'phone')}),
        ('Способ связи', {
            'fields': ('contact_method', 'contact_value'),
            'description': _(
                'Контактные данные клиента (телефон, Telegram, WhatsApp, Viber, email). '
                'Для способа «Телефон» значение дублируется в поле «Phone» выше.'
            ),
        }),
        ('Сообщение', {'fields': ('message',)}),
        ('Статус', {'fields': ('status',)}),
        ('Системная информация', {
            'fields': (
                'turnstile_verified',
                'created_at', 'updated_at', 'user_agent', 'ip_address', 'referer',
            ),
            'classes': ('collapse',),
        }),
    )


# ============================================================
# 15. MISSION
# ============================================================

@admin.register(Mission)
class MissionAdmin(TranslationAdmin):
    list_display = ['page', 'title', 'is_active', 'order']
    list_filter = ['page', 'is_active']
    search_fields = ['title', 'subtitle', 'description']
    list_editable = ['is_active', 'order']

    fieldsets = (
        ('Страница', {'fields': ('page',)}),
        ('Заголовки', {'fields': ('title', 'subtitle', 'description')}),
        ('Фон', {
            'fields': ('background_light', 'background_dark'),
            'description': _('Загрузите фоновые изображения для светлой и тёмной темы'),
        }),
        ('Кнопка', {'fields': ('button_text', 'button_url'), 'classes': ('collapse',)}),
        ('Статус', {'fields': ('is_active', 'order')}),
    )


# ============================================================
# 16. SITE CONFIGURATION
# ============================================================

@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(BaseAdmin):
    list_display = ['site_name', 'is_maintenance_mode']
    list_filter = ['is_maintenance_mode']

    fieldsets = (
        ('Информация о сайте', {'fields': ('site_name', 'site_description')}),
        ('Логотипы', {
            'fields': ('logo_light', 'logo_dark', 'favicon'),
            'description': _('Логотипы для разных тем и favicon сайта'),
        }),
        ('OG Image', {'fields': ('og_image',), 'classes': ('collapse',)}),
        ('SEO по умолчанию', {
            'fields': ('default_seo_title', 'default_seo_description'),
            'classes': ('collapse',),
            'description': _('Используется как fallback, если у страницы нет SEO'),
        }),
        ('Режим обслуживания', {
            'fields': ('is_maintenance_mode', 'maintenance_text'),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        return not SiteConfiguration.objects.exists()


# ============================================================
# 17. PAGE SEO
# ============================================================

@admin.register(PageSEO)
class PageSEOAdmin(BaseAdmin):
    """
    Админка SEO-настроек страниц.

    Активные записи: home, contact, blog.
    Зарезервированные (секции главной): portfolio, about, services, pricing.
    """

    list_display = [
        'page_key_display',
        'title_preview_ru',
        'title_preview_en',
        'is_active',
        'is_reserved',
        'updated_at',
    ]
    list_filter = ['is_active', 'page_key']
    search_fields = ['page_key', 'title_ru', 'title_en', 'description_ru', 'description_en']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at', 'is_reserved_warning']

    fieldsets = (
        ('Страница', {
            'fields': ('page_key', 'is_active', 'is_reserved_warning'),
            'description': _(
                '«Активные» страницы: Главная, Контакты, Блог. '
                '«Зарезервированные» (Портфолио, О нас, Услуги, Тарифы) — секции на других страницах. '
                'Их SEO пока не выводится, но готово к использованию, когда появятся отдельные URL.'
            ),
        }),
        ('SEO — Русский', {
            'fields': ('title_ru', 'description_ru', 'keywords_ru'),
            'classes': ('wide',),
            'description': _(
                'Если оставить поля пустыми — будут использованы '
                'значения по умолчанию из <code>agency/seo_defaults.py</code>'
            ),
        }),
        ('SEO — English', {
            'fields': ('title_en', 'description_en', 'keywords_en'),
            'classes': ('wide',),
            'description': _(
                'Если поля пусты — будет использован русский вариант или fallback'
            ),
        }),
        ('Open Graph (опционально)', {
            'fields': ('og_title_ru', 'og_description_ru', 'og_title_en', 'og_description_en'),
            'classes': ('collapse',),
            'description': _('Если пусто — используется SEO Title/Description страницы'),
        }),
        ('Служебное', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    # Ключи, которые сейчас реально выводятся
    ACTIVE_PAGE_KEYS = {'home', 'contact', 'blog'}

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'title_ru' in form.base_fields:
            form.base_fields['title_ru'].widget.attrs['maxlength'] = 200
            form.base_fields['title_ru'].widget.attrs['placeholder'] = 'Рекомендуемая длина: 50–60 символов'
        if 'title_en' in form.base_fields:
            form.base_fields['title_en'].widget.attrs['maxlength'] = 200
            form.base_fields['title_en'].widget.attrs['placeholder'] = 'Recommended: 50–60 characters'
        return form

    # ============================================================
    # DISPLAY HELPERS
    # ============================================================

    @admin.display(description=_('Страница'), ordering='page_key')
    def page_key_display(self, obj):
        return obj.get_page_key_display()

    @admin.display(description=_('Статус использования'), boolean=False)
    def is_reserved(self, obj):
        """Показывает, активна ли страница сейчас или зарезервирована на будущее."""
        if obj.page_key in self.ACTIVE_PAGE_KEYS:
            return format_html(
                '<span style="color:#2ecc71;font-weight:600;">✓ Активна</span>'
            )
        return format_html(
            '<span style="color:#999;font-style:italic;">⋯ Зарезервирована</span>'
        )

    @admin.display(description=_('Информация'))
    def is_reserved_warning(self, obj):
        """Информационный блок в форме редактирования."""
        if obj and obj.page_key in self.ACTIVE_PAGE_KEYS:
            return format_html(
                '<div style="padding:8px 12px;background:rgba(46,204,113,0.1);'
                'border-left:3px solid #2ecc71;border-radius:4px;color:#2ecc71;">'
                '<strong>✓ Активная страница.</strong> SEO выводится в шаблонах.'
                '</div>'
            )
        if obj:
            return format_html(
                '<div style="padding:8px 12px;background:rgba(243,156,18,0.1);'
                'border-left:3px solid #f39c12;border-radius:4px;color:#e67e22;">'
                '<strong>⋯ Зарезервированная страница.</strong> '
                'SEO пока не выводится — соответствующий контент является секцией другой страницы. '
                'Можно заполнить заранее — заработает, когда появится отдельный URL и вью.'
                '</div>'
            )
        return format_html(
            '<div style="padding:8px 12px;background:rgba(52,152,219,0.1);'
            'border-left:3px solid #3498db;border-radius:4px;color:#2980b9;">'
            'Создайте новую запись или отредактируйте существующую.'
            '</div>'
        )

    @admin.display(description=_('Title (RU)'))
    def title_preview_ru(self, obj):
        title = obj.title_ru or get_default_seo(obj.page_key, 'ru').get('title', '')
        length = len(title)
        color = '#2ecc71' if 40 <= length <= 60 else ('#f39c12' if length <= 70 else '#e74c3c')
        preview = title[:60] + ('…' if len(title) > 60 else '')
        return format_html(
            '<span title="{}">{}</span> <small style="color:{};">({} симв.)</small>',
            title, preview, color, length
        )

    @admin.display(description=_('Title (EN)'))
    def title_preview_en(self, obj):
        title = obj.title_en or ''
        if not title:
            return format_html('<span style="opacity:0.5;">— не задано —</span>')
        length = len(title)
        color = '#2ecc71' if 40 <= length <= 60 else ('#f39c12' if length <= 70 else '#e74c3c')
        preview = title[:60] + ('…' if len(title) > 60 else '')
        return format_html(
            '<span title="{}">{}</span> <small style="color:{};">({} симв.)</small>',
            title, preview, color, length
        )

# ============================================================
# 18. TELEGRAM LOGS
# ============================================================

@admin.register(TelegramLog)
class TelegramLogAdmin(BaseAdmin):
    list_display = ['log_type', 'chat_id', 'is_sent', 'created_at']
    list_filter = ['log_type', 'is_sent', 'created_at']
    search_fields = ['chat_id', 'message', 'error']
    readonly_fields = ['log_type', 'chat_id', 'message', 'is_sent', 'error', 'created_at']
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ============================================================
# SUBSCRIBERS
# ============================================================

@admin.register(Subscriber)
class SubscriberAdmin(BaseAdmin):
    list_display = ['email', 'is_active', 'source', 'created_at', 'last_emailed_at']
    list_filter = ['is_active', 'source', 'created_at']
    search_fields = ['email', 'ip_address']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at', 'ip_address', 'user_agent', 'unsubscribe_token', 'unsubscribed_at']
    date_hierarchy = 'created_at'

    actions = [
        set_active_true,
        set_active_false,
        export_selected_as_csv,
        export_selected_as_json,
    ]

    fieldsets = (
        ('Подписчик', {'fields': ('email', 'is_active', 'source')}),
        ('Отписка', {
            'fields': ('unsubscribe_token', 'unsubscribed_at'),
            'classes': ('collapse',),
        }),
        ('Рассылка', {
            'fields': ('last_emailed_at',),
            'classes': ('collapse',),
        }),
        ('Системная информация', {
            'fields': ('ip_address', 'user_agent', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )