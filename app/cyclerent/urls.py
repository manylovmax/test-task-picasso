from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from rents import views

router = routers.DefaultRouter()
router.register(r'rents', views.RentViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user-create/', views.create_user, name='user_create'),
    path('bikes-for-rent/', views.bikes_for_rent, name='bikes_for_rent'),
    path('rent-the-bike/<int:pk>', views.rent_the_bike, name='rent_the_bike'),
    path('finish-the-rent/<int:pk>', views.finish_the_rent, name='finish_the_rent'),
]
