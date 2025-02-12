import factory
from unittest.mock import patch
from faker import Faker

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from api.users.models import User, Category
from api.notes.models import Note
from .factories import UserFactory, CategoryFactory

fake = Faker()


class TestUserListTestCase(APITestCase):
    """
    Tests /users list operations.
    """

    def setUp(self):
        self.url = reverse('user-list')
        self.user_data = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'password': fake.password(),
        }

    def test_post_request_with_no_data_fails(self):
        """"
        Test that a POST request with no data fails.
        """
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_request_with_valid_data_succeeds(self):
        """
        Test that a POST request with valid data succeeds.
        """
        response = self.client.post(
            self.url, self.user_data,
            HTTP_ORIGIN='http://new.example.com'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(pk=response.data.get('id'))
        self.assertEqual(user.email, self.user_data.get('email'))
        self.assertEqual(user.first_name, self.user_data.get('first_name'))
        self.assertEqual(user.last_name, self.user_data.get('last_name'))


class TestUserDetailTestCase(APITestCase):
    """
    Tests /users detail operations.
    """

    def setUp(self):
        self.user = UserFactory()
        self.url = reverse('user-detail', kwargs={'pk': self.user.pk})
        self.client.force_authenticate(user=self.user)

    def test_get_request_returns_a_given_user(self):
        """
        Test that a GET request returns a given user.
        """
        response = self.client.get(
            self.url, HTTP_ORIGIN='http://new.example.com'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_request_updates_a_user(self):
        """
        Test that a PUT request updates a user.
        """
        new_first_name = fake.first_name()
        payload = {'first_name': new_first_name}
        response = self.client.put(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that the user was updated
        user = User.objects.get(pk=self.user.id)
        self.assertEqual(user.first_name, new_first_name)


class CurrentUserViewTest(APITestCase):
    """
    Tests for the /users/me endpoint.
    """

    def test_get_current_user(self):
        """
        Test that a GET request to the /users/me/ endpoint returns the 
        currently authenticated user.
        """
        user = UserFactory()
        self.client.force_authenticate(user=user)
        url = reverse('user-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], user.email)


class RegistrationViewTest(APITestCase):
    """
    Test suite for registration endpoint
    """
    def setUp(self):
        self.url = reverse('register')
        self.valid_payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_valid_registration(self):
        """Test registration with valid data"""
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.valid_payload['email']).exists())
        self.assertIn('user', response.data)
        self.assertIn('message', response.data)

    def test_invalid_email_format(self):
        """Test registration with invalid email format"""
        payload = self.valid_payload.copy()
        payload['email'] = 'invalid-email'
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['errors'])

    def test_duplicate_email(self):
        """Test registration with existing email"""
        UserFactory(email=self.valid_payload['email'])
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['errors'])

    def test_missing_required_fields(self):
        """Test registration with missing fields"""
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['errors'])
        self.assertIn('password', response.data['errors'])


class TestCategoryViewSet(APITestCase):
    """
    Test suite for Category ViewSet
    """
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.category = CategoryFactory()
        Note.objects.create(title="Test Note", category=self.category, user=self.user)
        self.url = reverse('category-list')

    def test_list_categories(self):
        """Test listing all public categories"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.category.id)
        self.assertEqual(response.data[0]['note_count'], 1)

    def test_create_category(self):
        """Test creating a category"""
        data = {'name': 'New Category', 'color': '#FF0000'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], data['name'])

    def test_update_category(self):
        """Test updating a category"""
        url = reverse('category-detail', kwargs={'pk': self.category.pk})
        data = {'name': 'Updated Category', 'color': '#00FF00'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, data['name'])

    def test_delete_category(self):
        """Test deleting a category"""
        url = reverse('category-detail', kwargs={'pk': self.category.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_access_any_category(self):
        """Test that users can access any public category"""
        other_category = CategoryFactory()
        url = reverse('category-detail', kwargs={'pk': other_category.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_any_category(self):
        """Test that any user can update any category"""
        other_category = CategoryFactory()
        url = reverse('category-detail', kwargs={'pk': other_category.pk})
        data = {'name': 'Updated Public Category', 'color': '#123456'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        other_category.refresh_from_db()
        self.assertEqual(other_category.name, data['name'])
