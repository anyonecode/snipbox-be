"""
Tests for the SnipBox snippets app.

Covers JWT auth, snippet CRUD, ownership enforcement,
tag deduplication, tag list, and tag detail endpoints.
"""
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Snippet, Tag


def get_tokens_for_user(user):
    """Helper to get JWT access token for a user."""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


class AuthenticationTests(APITestCase):
    """Tests for JWT login and token refresh endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
        )

    def test_login_success(self):
        response = self.client.post('/api/v1/token/', {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post('/api/v1/token/', {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post('/api/v1/token/refresh/', {
            'refresh': str(refresh),
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class SnippetOverviewCreateTests(APITestCase):
    """Tests for the overview (GET) and create (POST) endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            password='pass123',
        )
        self.token = get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_overview_empty(self):
        response = self.client.get('/api/v1/snippets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 0)
        self.assertEqual(response.data['snippets'], [])

    def test_create_snippet(self):
        data = {
            'title': 'Test Snippet',
            'note': 'This is a test note.',
            'tags': [{'title': 'django'}],
        }
        response = self.client.post('/api/v1/snippets/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Snippet')
        self.assertEqual(len(response.data['tags']), 1)
        self.assertEqual(response.data['tags'][0]['title'], 'django')

    def test_overview_count(self):
        Snippet.objects.create(title='A', note='Note A', user=self.user)
        Snippet.objects.create(title='B', note='Note B', user=self.user)
        response = self.client.get('/api/v1/snippets/')
        self.assertEqual(response.data['total'], 2)
        self.assertEqual(len(response.data['snippets']), 2)

    def test_unauthenticated_access_denied(self):
        self.client.credentials()
        response = self.client.get('/api/v1/snippets/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TagDeduplicationTests(APITestCase):
    """Tests that tag deduplication works correctly."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='bob',
            password='pass123',
        )
        self.token = get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_same_tag_not_duplicated(self):
        """Creating two snippets with the same tag title should result in one tag."""
        data1 = {'title': 'Snippet 1', 'note': 'Note 1', 'tags': [{'title': 'python'}]}
        data2 = {'title': 'Snippet 2', 'note': 'Note 2', 'tags': [{'title': 'python'}]}
        self.client.post('/api/v1/snippets/', data1, format='json')
        self.client.post('/api/v1/snippets/', data2, format='json')
        self.assertEqual(Tag.objects.filter(title='python').count(), 1)

    def test_different_tags_created(self):
        data = {
            'title': 'Multi-tag',
            'note': 'Has two tags',
            'tags': [{'title': 'tag1'}, {'title': 'tag2'}],
        }
        self.client.post('/api/v1/snippets/', data, format='json')
        self.assertEqual(Tag.objects.count(), 2)


class SnippetDetailUpdateDeleteTests(APITestCase):
    """Tests for detail, update, and delete endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='carol',
            password='pass123',
        )
        self.other_user = User.objects.create_user(
            username='dave',
            password='pass123',
        )
        self.token = get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.snippet = Snippet.objects.create(
            title='My Snippet',
            note='My note',
            user=self.user,
        )
        self.other_snippet = Snippet.objects.create(
            title='Dave Snippet',
            note='Dave note',
            user=self.other_user,
        )

    def test_get_own_snippet(self):
        response = self.client.get(f'/api/v1/snippets/{self.snippet.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'My Snippet')

    def test_cannot_access_other_user_snippet(self):
        response = self.client.get(f'/api/v1/snippets/{self.other_snippet.pk}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_snippet(self):
        data = {'title': 'Updated Title', 'note': 'Updated note'}
        response = self.client.put(
            f'/api/v1/snippets/{self.snippet.pk}/',
            data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

    def test_partial_update_snippet(self):
        response = self.client.patch(
            f'/api/v1/snippets/{self.snippet.pk}/',
            {'title': 'Patched Title'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Patched Title')

    def test_delete_snippet_returns_remaining(self):
        Snippet.objects.create(title='Remaining', note='Still here', user=self.user)
        response = self.client.delete(f'/api/v1/snippets/{self.snippet.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 1)

    def test_cannot_delete_other_user_snippet(self):
        response = self.client.delete(f'/api/v1/snippets/{self.other_snippet.pk}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TagTests(APITestCase):
    """Tests for tag list and tag detail endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='eve',
            password='pass123',
        )
        self.token = get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.tag_python = Tag.objects.create(title='python')
        self.tag_django = Tag.objects.create(title='django')
        self.snippet = Snippet.objects.create(
            title='Eve Snippet',
            note='Eve note',
            user=self.user,
        )
        self.snippet.tags.add(self.tag_python)

    def test_tag_list(self):
        response = self.client.get('/api/v1/tags/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_tag_detail_returns_linked_snippets(self):
        response = self.client.get(f'/api/v1/tags/{self.tag_python.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tag']['title'], 'python')
        self.assertEqual(response.data['total_snippets'], 1)

    def test_tag_detail_no_snippets_for_other_tag(self):
        response = self.client.get(f'/api/v1/tags/{self.tag_django.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_snippets'], 0)

    def test_tag_not_found(self):
        response = self.client.get('/api/v1/tags/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
