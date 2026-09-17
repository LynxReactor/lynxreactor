# agency/tests/test_blog_vote.py

import json
import pytest
from django.core.cache import cache
from django.urls import reverse

from agency.models import BlogPostVote


@pytest.fixture(autouse=True)
def clear_rate_limit():
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
class TestBlogVote:
    def _vote(self, client, post, vote_type='like'):
        url = reverse('agency:blog_post_vote_by_id', kwargs={'post_id': post.id})
        return client.post(
            url,
            data=json.dumps({'vote_type': vote_type}),
            content_type='application/json',
        )

    def test_first_like_increments_likes(self, client, blog_post):
        response = self._vote(client, blog_post, 'like')
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['action'] == 'added'
        assert data['likes'] == 1
        assert data['dislikes'] == 0
        assert data['user_vote'] == 'like'

    def test_first_dislike_increments_dislikes(self, client, blog_post):
        response = self._vote(client, blog_post, 'dislike')
        assert response.status_code == 200
        data = response.json()
        assert data['action'] == 'added'
        assert data['likes'] == 0
        assert data['dislikes'] == 1

    def test_same_vote_twice_removes_vote(self, client, blog_post):
        self._vote(client, blog_post, 'like')
        response = self._vote(client, blog_post, 'like')
        assert response.status_code == 200
        data = response.json()
        assert data['action'] == 'removed'
        assert data['likes'] == 0
        assert data['user_vote'] is None

    def test_changing_vote_from_like_to_dislike(self, client, blog_post):
        self._vote(client, blog_post, 'like')
        response = self._vote(client, blog_post, 'dislike')
        assert response.status_code == 200
        data = response.json()
        assert data['action'] == 'changed'
        assert data['likes'] == 0
        assert data['dislikes'] == 1
        assert data['user_vote'] == 'dislike'

    def test_invalid_vote_type_returns_400(self, client, blog_post):
        response = self._vote(client, blog_post, 'invalid')
        assert response.status_code == 400

    def test_invalid_json_returns_400(self, client, blog_post):
        url = reverse('agency:blog_post_vote_by_id', kwargs={'post_id': blog_post.id})
        response = client.post(url, data='not json', content_type='application/json')
        assert response.status_code == 400

    def test_404_for_nonexistent_post(self, client):
        url = reverse('agency:blog_post_vote_by_id', kwargs={'post_id': 99999})
        response = client.post(
            url,
            data=json.dumps({'vote_type': 'like'}),
            content_type='application/json',
        )
        assert response.status_code == 404

    def test_rate_limit_blocks_after_20_votes(self, client, blog_post):
        # 20 голосов — ок
        for i in range(20):
            response = self._vote(client, blog_post, 'like' if i % 2 == 0 else 'dislike')
            assert response.status_code == 200, f'Failed at attempt {i+1}'
        # 21-й — заблокирован
        response = self._vote(client, blog_post, 'like')
        assert response.status_code == 429