from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from rents.models import Bike, Rent
from rents.serializers import BikeSerializer, RentSerializer


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


class bikes_for_rent_ViewTest(TestCase):

    def setUp(self):
        #Создание пользователя
        User.objects.create_user(username='testuser1', password='12345')
        Bike.objects.create(brand='Brand 1', model='Model 1', price_per_hour=100)
        Bike.objects.create(brand='Brand 2', model='Model 2', price_per_hour=200)

    def test_success(self):
        client = APIClient()
        resp = client.post('/api/token/', {'username': 'testuser1', 'password': '12345'}, format='json')
        token = resp.data['access']
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        resp = client.get('/bikes-for-rent/')
        self.assertEqual(resp.status_code, 200)
        expected_data = BikeSerializer(Bike.objects.filter(is_rent=False).all(), many=True).data
        self.assertEqual(resp.data, expected_data)

    def test_one_rent(self):
        client = APIClient()
        resp = client.post('/api/token/', {'username': 'testuser1', 'password': '12345'}, format='json')
        token = resp.data['access']
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        bike = Bike.objects.filter(brand='Brand 1').first()
        bike.is_rent = True
        bike.save()
        resp = client.get('/bikes-for-rent/')
        self.assertEqual(resp.status_code, 200)
        expected_data = BikeSerializer(Bike.objects.filter(is_rent=False).all(), many=True).data
        self.assertEqual(resp.data, expected_data)
