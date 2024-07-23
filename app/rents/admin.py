from django.contrib import admin

# Register your models here.
from .models import Rent, Bike

class BikeAdmin(admin.ModelAdmin):
    fields = ["model", "brand", "price_per_hour", "is_rent"]
    list_display = ["id", "brand", "model", "price_per_hour", "is_rent"]


admin.site.register(Bike, BikeAdmin)

class RentAdmin(admin.ModelAdmin):
    fields = ["user", "bike", "start_at", "finish_at", "price", "paid"]
    list_display = ["id", "user", "bike", "start_at", "finish_at", "price", "paid"]


admin.site.register(Rent, RentAdmin)
