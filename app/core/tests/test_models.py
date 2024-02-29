#  test models

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from .. import models


class ModelTest(TestCase):
    # test models

    def test_create_user_with_email_successful(self):
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))  # checked hashed password not the row one

    def test_new_user_email_normalized(self):
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]  # it's normal to have first part of the email capital but not after the @
        for email, expected in sample_emails:
            # in 2D arrays use email as first value and expected as second value in for loop
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_no_email_raise_error(self):
        with self.assertRaises(ValueError):  # checks if this will raise a value error when what is below happens
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser('test@example.com', 'test123')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """test create recipe is successful"""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'),  # decimal not good for real finance application
            description='sample recipe description',
        )
        self.assertEqual(str(recipe), recipe.title)
