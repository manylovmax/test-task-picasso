from datetime import datetime

from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


from rents.serializers import UserSerializer, BikeSerializer, RentSerializer
from rents.models import Bike, Rent

from rents.tasks import calculate_price


@api_view(['POST'])
def register(request):
    serialized = UserSerializer(data=request.data)
    if serialized.is_valid():
        User.objects.create_user(
            serialized.data['username'],
            serialized.data['email'],
            serialized.data['password']
        )
        return Response({'detail': 'Пользователь зарегистрирован'}, status=status.HTTP_201_CREATED)
    else:
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bikes_for_rent(request: Request):
    serializer = BikeSerializer(Bike.objects.filter(is_rent=False).order_by('brand'), many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rent_the_bike(request: Request, pk: int):
    rent = Rent.objects.filter(user=request.user, paid=False).first()
    if rent:
        return Response({'detail': 'Нельзя арендовать больше велосипедов. Сначала оплатите аренду'}, status=status.HTTP_200_OK)
    bike = Bike.objects.filter(pk=pk).first()
    if not bike:
        return Response({'detail': 'Велосипед не найден'}, status=status.HTTP_404_NOT_FOUND)
    if bike.is_rent:
        return Response({'detail': 'Велосипед арендован'}, status=status.HTTP_200_OK)
    
    bike.is_rent = True
    bike.save()


    rent = Rent(user=request.user, bike=bike, start_at=datetime.now())
    rent.save()

    return Response({}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def finish_the_rent(request: Request, pk: int):
    rent = Rent.objects.filter(pk=pk, user=request.user).first()
    if not rent:
        return Response({'detail': 'Запись об аренде не найдена'}, status=status.HTTP_404_NOT_FOUND)
    
    if rent.finish_at:
        return Response({'detail': 'Аренда уже завершена'}, status=status.HTTP_200_OK)
    
    rent.bike.is_rent = False
    rent.bike.save()

    rent.finish_at = datetime.now()
    rent.save()
    calculate_price.delay(rent.id)

    return Response({}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_rent_price(request: Request, pk: int):
    rent = Rent.objects.filter(pk=pk, user=request.user).first()
    if not rent:    
        return Response({'detail': 'Запись об аренде не найдена'}, status=status.HTTP_404_NOT_FOUND)
    
    if not rent.price:
        return Response({'detail': 'Цена аренды еще не подсчитана'}, status=status.HTTP_200_OK)

    return Response({'rent_price': rent.price}, status=status.HTTP_200_OK)
        

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pay_for_rent(request: Request, pk: int):
    rent = Rent.objects.filter(pk=pk, user=request.user).select_related('bike', 'user').first()
    if not rent:
        return Response({'detail': 'Запись об аренде не найдена'}, status=status.HTTP_404_NOT_FOUND)
    
    if not rent.price:
        return Response({'detail': 'Цена аренды еще не подсчитана'}, status=status.HTTP_200_OK)
    
    if rent.paid:
        return Response({'detail': 'Аренда уже оплачена'}, status=status.HTTP_200_OK)
    
    rent.paid = True
    rent.save()
    data = RentSerializer(rent).data
    data['user'] = rent.user.username
    data['bike'] = ' '.join([rent.bike.brand, rent.bike.model])

    return Response(data, status=status.HTTP_200_OK)
        

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_rents(request: Request):
    rents = Rent.objects.filter(user=request.user).select_related('bike', 'user').all()
    
    data = list()
    for rent in rents:
        r = RentSerializer(rent).data
        r['bike'] = ' '.join([rent.bike.brand, rent.bike.model])
        r['user'] = rent.user.username
        data.append(r)
        

    return Response(data, status=status.HTTP_200_OK)
