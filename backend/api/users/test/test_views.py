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
    Test suite for Category ViewSet where categories
    can be either global (user=None) or user-owned.
    """

    def setUp(self):
        # Authenticated user
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

        # Create a global category (user=None)
        self.global_category = CategoryFactory(user=None)

        # Create a category owned by the authenticated user
        self.user_category = CategoryFactory(user=self.user)
        Note.objects.create(title="Test Note", category=self.user_category, user=self.user)

        # Create a category owned by a different user
        self.other_user = UserFactory()
        self.other_user_category = CategoryFactory(user=self.other_user)

        # Base URL for listing or creating categories
        self.url_list = reverse('category-list')
        # Detail URL for the user_category
        self.url_detail_user = reverse('category-detail', kwargs={'pk': self.user_category.pk})
        # Detail URL for the global category
        self.url_detail_global = reverse('category-detail', kwargs={'pk': self.global_category.pk})
        # Detail URL for the other_user category
        self.url_detail_other = reverse('category-detail', kwargs={'pk': self.other_user_category.pk})

    def test_list_includes_global_and_user_owned(self):
        """
        The authenticated user should see both:
         - Global categories (user=None)
         - Their own categories
         - NOT another user's categories
        """
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [cat['id'] for cat in response.data]
        # Expect to see the global category and the user's category
        self.assertIn(self.global_category.id, returned_ids)
        self.assertIn(self.user_category.id, returned_ids)
        # Should NOT see the other user's category
        self.assertNotIn(self.other_user_category.id, returned_ids)

    def test_list_includes_note_count(self):
        """
        Confirm note_count is returned properly for categories.
        """
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Look up the user's category from the response
        user_cat = next((c for c in response.data if c['id'] == self.user_category.id), None)
        self.assertIsNotNone(user_cat)
        self.assertEqual(user_cat['note_count'], 1)  # We created 1 Note above

    def test_create_category_assigned_to_user(self):
        """
        Creating a category should automatically assign it to the authenticated user,
        unless your backend logic explicitly allows user=None.
        """
        data = {'name': 'Brand New Category', 'color': '#FF0000'}
        response = self.client.post(self.url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_cat_id = response.data['id']
        new_cat = Category.objects.get(pk=new_cat_id)
        self.assertEqual(str(new_cat.user_id), str(self.user.id))
        self.assertEqual(new_cat.name, data['name'])
        self.assertEqual(new_cat.color, data['color'])

    def test_read_global_category(self):
        """
        Ensure the authenticated user can GET a global category detail.
        """
        response = self.client.get(self.url_detail_global)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.global_category.id)

    def test_read_other_users_category_fails_or_succeeds(self):
        """
        Depending on your policy, users might or might not read others' categories.
        If you allow read access to all categories, test for 200.
        Otherwise, test for 404 or 403. Adjust as needed.
        """
        response = self.client.get(self.url_detail_other)
        # If your policy blocks access to other user's categories, expect a 404 or 403:
        # self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # If your policy allows reading them (like "public"), expect 200:
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_user_own_category(self):
        """
        Users should be able to update their own categories.
        """
        data = {'name': 'Updated Category', 'color': '#00FF00'}
        response = self.client.put(self.url_detail_user, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user_category.refresh_from_db()
        self.assertEqual(self.user_category.name, data['name'])

    def test_update_global_category(self):
        """
        If your policy allows it, the user can update a global category. If not, expect 403.
        """
        data = {'name': 'Updated Global Category', 'color': '#123456'}
        response = self.client.put(self.url_detail_global, data, format='json')
        # Adjust based on your real policy:
        # If allowed:
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.global_category.refresh_from_db()
        self.assertEqual(self.global_category.name, data['name'])
        # If not allowed, you'd do:
        # self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_category(self):
        """
        Deleting the user's own category should succeed.
        """
        response = self.client.delete(self.url_detail_user)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=self.user_category.pk).exists())

    def test_delete_global_category(self):
        """
        Adjust test logic if you allow or disallow global category deletion.
        """
        response = self.client.delete(self.url_detail_global)
        # If policy disallows deletion of global categories:
        # self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # If policy allows it:
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=self.global_category.pk).exists())
