from django.test import TestCase

# Create your tests here.

from rents.models import Bike, Rent


class RegisterViewTest(TestCase):

    def test_success(self):
        data = {'username': 'test_user', 'password': 'test_password', 'email': 'test_email@test.com'}
        resp = self.client.post('/register/', data)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json(), {"detail": "Пользователь зарегистрирован"})

    def test_no_username(self):
        data = {'password': 'test_password', 'email': 'test_email@test.com'}
        resp = self.client.post('/register/', data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {"username": ["Обязательное поле."]})

    def test_no_password(self):
        data = {'username': 'test_user', 'email': 'test_email@test.com'}
        resp = self.client.post('/register/', data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {"password": ["Обязательное поле."]})

    def test_no_email(self):
        data = {'username': 'test_user', 'password': 'test_password'}
        resp = self.client.post('/register/', data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {"email": ["Обязательное поле."]})
