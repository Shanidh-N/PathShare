from django.contrib import admin
from .models import Customer, all_rides

admin.site.register(Customer)
admin.site.register(all_rides)

