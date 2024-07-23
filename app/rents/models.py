from django.db import models
from django.contrib.auth.models import User


class Bike(models.Model):
    model = models.CharField(blank=False)
    brand = models.CharField(blank=False)
    price_per_hour = models.FloatField(blank=False)
    is_rent = models.BooleanField(default=False)

    def __str__(self):
        return " ".join([self.brand, self.model])


class Rent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    bike = models.ForeignKey(Bike, on_delete=models.DO_NOTHING, blank=False)
    start_at = models.DateTimeField(blank=False)
    finish_at = models.DateTimeField(blank=True, null=True)
    price = models.FloatField(null=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk)