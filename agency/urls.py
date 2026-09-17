# agency/urls.py

from django.urls import path, re_path
from django.conf import settings
from django.views.generic import TemplateView

from .views import (
    IndexView,
    ContactView,
    BlogListView,
    BlogDetailView,
    BlogCategoryView,
    ajax_contact,
    ajax_subscribe,
    unsubscribe_view,
    toggle_theme,
    robots_txt,
    maintenance_view,
    blog_post_vote,
    blog_post_vote_by_id,
)

app_name = 'agency'

urlpatterns = [
    # ============================================================
    # MAIN PAGES
    # ============================================================
    path('', IndexView.as_view(), name='home'),
    path('contact/', ContactView.as_view(), name='contact'),

    # ============================================================
    # BLOG
    # ============================================================
    path('blog/', BlogListView.as_view(), name='blog'),
    path('blog/category/<slug:slug>/', BlogCategoryView.as_view(), name='blog_category'),
    path('blog/<slug:slug>/', BlogDetailView.as_view(), name='blog_detail'),
    # Голосование за пост
    path('blog/<slug:slug>/vote/', blog_post_vote, name='blog_post_vote'),
    path('blog/vote/<int:post_id>/', blog_post_vote_by_id, name='blog_post_vote_by_id'),

    # ============================================================
    # AJAX ENDPOINTS
    # ============================================================
    path('api/contact/', ajax_contact, name='ajax_contact'),
    path('api/subscribe/', ajax_subscribe, name='ajax_subscribe'),
    path('unsubscribe/', unsubscribe_view, name='unsubscribe'),
    path('toggle-theme/', toggle_theme, name='toggle_theme'),

    # ============================================================
    # STATIC PAGES
    # ============================================================
    path('thanks/', TemplateView.as_view(template_name='agency/thanks.html'), name='thanks'),
    path('maintenance/', maintenance_view, name='maintenance'),

    # ============================================================
    # SEO URLS
    # ============================================================
    path('robots.txt', robots_txt, name='robots'),
]
