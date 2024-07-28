import pytest

from unittest.mock import patch
from datetime import datetime

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
        # Авторизация
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
        # Авторизация
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


class TestRentTheBikeView:

    def setUp(self):
        user = User.objects.create_user(username='testuser1', password='12345')
        Bike.objects.create(brand='Brand 1', model='Model 1', price_per_hour=100)
        Bike.objects.create(brand='Brand 2', model='Model 2', price_per_hour=200)
        return user
    
    @pytest.mark.django_db
    def test_success(self):
        self.setUp()
        # Авторизация
        client = APIClient()
        resp = client.post('/api/token/', {'username': 'testuser1', 'password': '12345'}, format='json')
        token = resp.data['access']
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        bike = Bike.objects.first()
        resp = client.post('/rent-the-bike/' + str(bike.id))
        assert resp.status_code == 200
        bike.refresh_from_db()
        assert bike.is_rent == True
        rent = Rent.objects.filter(user__username='testuser1').first()
        assert rent.bike == bike

    @pytest.mark.django_db
    def test_bike_not_found(self):
        self.setUp()
        # Авторизация
        client = APIClient()
        resp = client.post('/api/token/', {'username': 'testuser1', 'password': '12345'}, format='json')
        token = resp.data['access']
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        resp = client.post('/rent-the-bike/' + '10')
        assert resp.status_code == 404
        assert resp.data == {'detail': 'Велосипед не найден'}

    @pytest.mark.django_db
    def test_bike_already_rent(self):
        self.setUp()
        # Авторизация
        client = APIClient()
        resp = client.post('/api/token/', {'username': 'testuser1', 'password': '12345'}, format='json')
        token = resp.data['access']
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        bike = Bike.objects.first()
        bike.is_rent = True
        bike.save()
        resp = client.post('/rent-the-bike/' + str(bike.id))
        assert resp.status_code == 200
        assert resp.data == {'detail': 'Велосипед арендован'}

    @pytest.mark.django_db
    def test_cannot_rent_more_bikes(self):
        user = self.setUp()
        # Авторизация
        client = APIClient()
        resp = client.post('/api/token/', {'username': 'testuser1', 'password': '12345'}, format='json')
        token = resp.data['access']
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        bike = Bike.objects.first()
        Rent.objects.create(user=user, bike=bike, start_at=datetime.now())
        resp = client.post('/rent-the-bike/' + str(bike.id))
        assert resp.status_code == 200
        assert resp.data == {'detail': 'Нельзя арендовать больше велосипедов. Сначала оплатите аренду'}


class TestFinishTheRentView:

    def setUp(self):
        user = User.objects.create_user(username='testuser1', password='12345')
        bike1 = Bike.objects.create(brand='Brand 1', model='Model 1', price_per_hour=100)
        Rent.objects.create(bike=bike1, user=user, start_at=datetime.now())
        return user
    
    @pytest.mark.django_db
    def test_success(self):
        user = self.setUp()
        # Авторизация
        client = APIClient()
        resp = client.post('/api/token/', {'username': 'testuser1', 'password': '12345'}, format='json')
        token = resp.data['access']
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        rent = Rent.objects.first()
        with patch('rents.views.calculate_price.delay') as mock_task:
            resp = client.post('/finish-the-rent/' + str(rent.id))
            assert mock_task.called
            now = datetime.now()
            assert resp.status_code == 200
            rent = Rent.objects.filter(user=user).first()
            assert rent.finish_at
            assert rent.bike.is_rent == False
    
    @pytest.mark.django_db
    def test_not_found(self):
        user = self.setUp()
        # Авторизация
        client = APIClient()
        resp = client.post('/api/token/', {'username': 'testuser1', 'password': '12345'}, format='json')
        token = resp.data['access']
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        resp = client.post('/finish-the-rent/100')
        assert resp.status_code == 404
        assert resp.data == {'detail': 'Запись об аренде не найдена'}


    @pytest.mark.django_db
    def test_rent_already_finished(self):
        user = self.setUp()
        # Авторизация
        client = APIClient()
        resp = client.post('/api/token/', {'username': 'testuser1', 'password': '12345'}, format='json')
        token = resp.data['access']
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        rent = Rent.objects.first()
        rent.finish_at = datetime.now()
        rent.save()
        resp = client.post('/finish-the-rent/' + str(rent.id))
        assert resp.status_code == 200
        assert resp.data == {'detail': 'Аренда уже завершена'}


class TestGetRentPriceView:

    def setUp(self):
        user = User.objects.create_user(username='testuser1', password='12345')
        bike1 = Bike.objects.create(brand='Brand 1', model='Model 1', price_per_hour=100)
        Rent.objects.create(bike=bike1, user=user, start_at=datetime.now(), price=100)
        return user
    
    @pytest.mark.django_db
    def test_success(self):
        user = self.setUp()
        # Авторизация
        client = APIClient()
        resp = client.post('/api/token/', {'username': 'testuser1', 'password': '12345'}, format='json')
        token = resp.data['access']
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        rent = Rent.objects.first()
        resp = client.get('/get-rent-price/' + str(rent.id))
        assert resp.status_code == 200
        assert resp.data == {'price': 100}

    
    @pytest.mark.django_db
    def test_not_found(self):
        user = self.setUp()
        # Авторизация
        client = APIClient()
        resp = client.post('/api/token/', {'username': 'testuser1', 'password': '12345'}, format='json')
        token = resp.data['access']
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        resp = client.get('/get-rent-price/100')
        assert resp.status_code == 404
        assert resp.data == {'detail': 'Запись об аренде не найдена'}

    
    @pytest.mark.django_db
    def test_price_not_calculated(self):
        user = self.setUp()
        # Авторизация
        client = APIClient()
        resp = client.post('/api/token/', {'username': 'testuser1', 'password': '12345'}, format='json')
        token = resp.data['access']
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        rent = Rent.objects.first()
        rent.price = None
        rent.save()
        resp = client.get('/get-rent-price/' + str(rent.id))
        assert resp.status_code == 200
        assert resp.data == {'detail': 'Цена аренды еще не подсчитана'}
