# agency/tests/test_newsletter.py

import pytest
from django.core import mail
from django.utils import timezone

from agency.models import Subscriber
from agency.tasks import send_blog_post_newsletter


@pytest.mark.django_db
class TestNewsletter:
    def test_newsletter_sends_to_active_subscribers(self, blog_post):
        s1 = Subscriber.objects.create(email='a@example.com', is_active=True)
        s2 = Subscriber.objects.create(email='b@example.com', is_active=True)

        result = send_blog_post_newsletter(blog_post.id)

        assert len(mail.outbox) == 2
        recipients = {m.to[0] for m in mail.outbox}
        assert recipients == {'a@example.com', 'b@example.com'}
        assert 'Newsletter' in result or 'sent' in result

    def test_newsletter_skips_inactive(self, blog_post):
        Subscriber.objects.create(email='active@example.com', is_active=True)
        Subscriber.objects.create(email='inactive@example.com', is_active=False)

        send_blog_post_newsletter(blog_post.id)

        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ['active@example.com']

    def test_newsletter_updates_last_emailed_at(self, blog_post, subscriber):
        assert subscriber.last_emailed_at is None
        send_blog_post_newsletter(blog_post.id)
        subscriber.refresh_from_db()
        assert subscriber.last_emailed_at is not None

    def test_newsletter_returns_early_if_no_subscribers(self, blog_post):
        result = send_blog_post_newsletter(blog_post.id)
        assert 'No active subscribers' in result
        assert len(mail.outbox) == 0

    def test_newsletter_only_for_published_post(self, draft_post, subscriber):
        result = send_blog_post_newsletter(draft_post.id)
        assert 'not found' in result.lower()
        assert len(mail.outbox) == 0