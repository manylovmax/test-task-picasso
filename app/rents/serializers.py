from django.contrib.auth.models import Group, User
from rest_framework import serializers

from rents.models import Bike, Rent


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'email': {'required': True}}


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class BikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bike
        fields = ['id', 'model', 'brand', 'price_per_hour', 'is_rent']


class RentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rent
        fields = ['id', 'user', 'bike', 'start_at', 'finish_at', 'price', 'paid']


    def create(self, validated_data):
        return Rent.objects.create(**validated_data)
