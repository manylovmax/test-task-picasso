from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from rents import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.register, name='register'),
    path('bikes-for-rent/', views.bikes_for_rent, name='bikes_for_rent'),
    path('rent-the-bike/<int:pk>', views.rent_the_bike, name='rent_the_bike'),
    path('finish-the-rent/<int:pk>', views.finish_the_rent, name='finish_the_rent'),
    path('get-rent-price/<int:pk>', views.get_rent_price, name='get_rent_price'),
    path('pay-for-rent/<int:pk>', views.pay_for_rent, name='pay_for_rent'),
    path('get-my-rents/', views.get_my_rents, name='get_my_rents'),
]
