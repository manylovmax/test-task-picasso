from datetime import datetime

from django.contrib.auth.models import User
from rest_framework import permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


from rents.serializers import UserSerializer, BikeSerializer, RentSerializer
from rents.models import Bike, Rent

from rents.tasks import count_price


@api_view(['POST'])
def create_user(request):
    serialized = UserSerializer(data=request.data)
    if serialized.is_valid():
        User.objects.create_user(
            serialized.data['username'],
            serialized.data['email'],
            serialized.data['password']
        )
        return Response(serialized.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)


class BikeViewSet(viewsets.ModelViewSet):
    queryset = Bike.objects.all().order_by('brand')
    serializer_class = BikeSerializer
    permission_classes = [permissions.AllowAny]


class RentViewSet(viewsets.ModelViewSet):
    queryset = Rent.objects.all().order_by('start_at')
    serializer_class = RentSerializer
    permission_classes = [permissions.AllowAny]


@api_view(['GET'])
#@permission_classes([IsAuthenticated])
def bikes_for_rent(request: Request):
    serializer = BikeSerializer(Bike.objects.filter(is_rent=False).order_by('brand'), many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
#@permission_classes([IsAuthenticated])
def rent_the_bike(request: Request, pk: int):
    user = User.objects.filter(username=request.user.username).first()
    if not user:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = UserSerializer(user)

    bike = Bike.objects.filter(pk=pk, is_rent=False).first()
    if not bike:
        return Response({'detail': 'Bike not found'}, status=status.HTTP_404_NOT_FOUND)
    if bike.is_rent:
        return Response({'detail': 'Bike is being rent'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    
    bike.is_rent = True
    bike.save()


    rent = Rent(user=request.user, bike=bike, start_at=datetime.now())
    rent.save()

    return Response({}, status=status.HTTP_200_OK)


@api_view(['POST'])
#@permission_classes([IsAuthenticated])
def finish_the_rent(request: Request, pk: int):
    rent = Rent.objects.filter(pk=pk, user=request.user).first()
    if not rent:
        return Response({'detail': 'Rent not found'}, status=status.HTTP_404_NOT_FOUND)
    
    rent.bike.is_rent = False
    rent.bike.save()

    rent.finish_at = datetime.now()
    rent.save()
    count_price.delay(rent.id)

    return Response({}, status=status.HTTP_200_OK)
