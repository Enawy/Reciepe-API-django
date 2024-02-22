# test for the user api

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """
    this is a helper function for
    creating user instead of creating users
    for every test over and over.

    **params can add any number of parameters (username, email, bio..etc.)
    in single dictionary for user data that gets created in here
    """
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """Test the public API related to user that requires no permissions"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }  # data of the new user created from the APIClient
        res = self.client.post(CREATE_USER_URL, payload)
        # post client with end point in CREATE_USER_URL and data in payload
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])  # get client from DB uses email similar to pyload
        self.assertTrue(user.check_password(payload['password']))  # checks if the pass in db and payload is the same
        self.assertNotIn('password', res.data)  # make sure that pass doesn't return in response for security

    def test_user_email_exists_error(self):
        """check if the user with email already exists"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        create_user(**payload)  # double * instead of typing email='email', password='password' amd so on
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pass_too_short_error(self):
        """test if the password entered is shorter than 8 chars"""
        payload = {
            'email': 'test@example.com',
            'password': 'pw345',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()  # return true if exists
        self.assertFalse(user_exists)  # make sure that he doesn't exist in the db

    def test_create_token_user(self):
        """Test generate token for valid credentials"""
        user_detail = {
            'name': 'test name',
            'email': 'test@example.com',
            'password': 'test-password123',
        }
        create_user(**user_detail)
        payload = {
            'email': user_detail['email'],
            'password': user_detail['password'],
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credit(self):
        """test return error if credentials is invalid"""
        create_user(email='test@example.com', password='goodpass')
        payload = {'email': 'test@example.com', 'password': 'wrong-pass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """test return error when password is blank"""
        payload = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test auth is required for user"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        # we are using a public user API test, so we don't have any authentication just try login with no credits


class PrivateUserAPITests(TestCase):
    """API test that requires Authentication"""

    # auth is handled in the setup def automatically

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='test name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """test return profile of the logged user"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'name': self.user.name, 'email': self.user.email})

    def test_post_me_not_allowed(self):
        """test post is not allowed for the ME endpoint"""
        res = self.client.post(ME_URL, {})  # make sure that this endpoint doesn't post any data
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """test update the user profile for the authentication user."""
        payload = {'name': 'updated name', 'password': 'newpassword123'}
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()  # for some reason you have to manually refresh the new data
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
