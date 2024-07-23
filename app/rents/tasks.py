# Create your tasks here
import math

from celery import shared_task
from rents.models import Rent


@shared_task
def count_price(rent_id: int):
    rent = Rent.objects.get(pk=rent_id)
    total_hours = math.ceil((rent.finish_at - rent.start_at).seconds/3600)
    rent.price = total_hours * rent.bike.price_per_hour
    rent.save()
    return
