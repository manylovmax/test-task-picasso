import pytest

from django.contrib.auth.models import User
from rest_framework.test import APIClient

from rents.models import Bike, Rent
from rents.serializers import BikeSerializer, RentSerializer


class TestRegisterView:

    @pytest.mark.django_db
    def test_success(self):
        data = {'username': 'test_user', 'password': 'test_password', 'email': 'test_email@test.com'}
        client = APIClient()
        resp = client.post('/register/', data, format='json')
        assert resp.status_code == 201
        assert resp.data == {"detail": "Пользователь зарегистрирован"}

    @pytest.mark.django_db
    def test_no_username(self):
        data = {'password': 'test_password', 'email': 'test_email@test.com'}
        client = APIClient()
        resp = client.post('/register/', data, format='json')
        assert resp.status_code == 400
        assert resp.data == {"username": ["Обязательное поле."]}

    @pytest.mark.django_db
    def test_no_password(self):
        data = {'username': 'test_user', 'email': 'test_email@test.com'}
        client = APIClient()
        resp = client.post('/register/', data, format='json')
        assert resp.status_code == 400
        assert resp.data == {"password": ["Обязательное поле."]}

    @pytest.mark.django_db
    def test_no_email(self):
        data = {'username': 'test_user', 'password': 'test_password'}
        client = APIClient()
        resp = client.post('/register/', data, format='json')
        assert resp.status_code == 400
        assert resp.data == {"email": ["Обязательное поле."]}


class TestBikesForRentView:

    @classmethod
    def setUp(cls):
        #Создание пользователя
        User.objects.create_user(username='testuser1', password='12345')
        Bike.objects.create(brand='Brand 1', model='Model 1', price_per_hour=100)
        Bike.objects.create(brand='Brand 2', model='Model 2', price_per_hour=200)
    
    @pytest.mark.django_db
    def test_success(self):
        self.setUp()
        client = APIClient()
        resp = client.post('/api/token/', {'username': 'testuser1', 'password': '12345'}, format='json')
        token = resp.data['access']
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        resp = client.get('/bikes-for-rent/')
        assert resp.status_code == 200
        expected_data = BikeSerializer(Bike.objects.filter(is_rent=False).all(), many=True).data
        assert resp.data == expected_data

    @pytest.mark.django_db
    def test_one_rent(self):
        self.setUp()
        client = APIClient()
        resp = client.post('/api/token/', {'username': 'testuser1', 'password': '12345'}, format='json')
        token = resp.data['access']
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        bike = Bike.objects.filter(brand='Brand 1').first()
        bike.is_rent = True
        bike.save()
        resp = client.get('/bikes-for-rent/')
        assert resp.status_code == 200
        expected_data = BikeSerializer(Bike.objects.filter(is_rent=False).all(), many=True).data
        assert resp.data == expected_data
