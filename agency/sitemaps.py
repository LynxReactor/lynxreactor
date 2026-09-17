# agency/sitemaps.py

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone

from .models import BlogPost


class BlogSitemap(Sitemap):
    """
    Sitemap для постов блога.

    Consistency: used __lte=now — как в BlogDetailView.
    Посты с published_at в будущем НЕ попадают в sitemap.
    """
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return BlogPost.objects.filter(
            is_active=True,
            is_published=True,
            published_at__lte=timezone.now(),
        ).order_by('-published_at')

    def lastmod(self, obj):
        return obj.updated_at or obj.published_at

    def location(self, obj):
        return f"/blog/{obj.slug}/"


class StaticViewSitemap(Sitemap):
    """
    Sitemap для статических страниц.
    """
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ['home', 'contact', 'blog']

    def location(self, item):
        return reverse(f'agency:{item}')