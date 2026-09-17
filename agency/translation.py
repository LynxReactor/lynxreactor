# agency/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import (
    HeroSection,
    ServicesSection, ServiceItem,
    TechSection, TechItem,
    Tariff,
    FAQSection, FAQItem,
    CTASection,
    ReviewsSection, Review,
    ContactPage,
    BlogCategory, BlogPost,
    Mission,
)


@register(HeroSection)
class HeroSectionTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle', 'description', 'cta_text', 'secondary_cta_text')


@register(ServicesSection)
class ServicesSectionTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle', 'description')


@register(ServiceItem)
class ServiceItemTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(TechSection)
class TechSectionTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle', 'description')


@register(TechItem)
class TechItemTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(Tariff)
class TariffTranslationOptions(TranslationOptions):
    fields = ('name', 'site_format', 'subtitle', 'description')


@register(FAQSection)
class FAQSectionTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle', 'description')


@register(FAQItem)
class FAQItemTranslationOptions(TranslationOptions):
    fields = ('question', 'answer', 'category')


@register(CTASection)
class CTASectionTranslationOptions(TranslationOptions):
    fields = ('title', 'badge', 'description', 'button_text', 'note')


@register(ReviewsSection)
class ReviewsSectionTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle', 'description')


@register(Review)
class ReviewTranslationOptions(TranslationOptions):
    fields = ('client_name', 'client_position', 'client_company', 'content')


@register(ContactPage)
class ContactPageTranslationOptions(TranslationOptions):
    fields = ('title', 'address', 'about_title', 'about_subtitle', 'about_text')


@register(BlogCategory)
class BlogCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(BlogPost)
class BlogPostTranslationOptions(TranslationOptions):
    fields = ('title', 'excerpt', 'content')


@register(Mission)
class MissionTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle', 'description', 'button_text')