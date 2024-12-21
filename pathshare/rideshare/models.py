from django.db import models
import random
import string

def generate_random_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

class Customer(models.Model):
    customer_id = models.CharField(max_length=8, default=generate_random_id, primary_key=True)
    customer_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    password = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    profile_pic = models.CharField(max_length=100)
    chats = models.JSONField(default=list) 
    previous_rides = models.JSONField(default=list)
    
    def __str__(self):
        return self.customer_name

""" # Driver model
class Driver(models.Model):
    driver_id = models.CharField(max_length=8, default=generate_random_id, primary_key=True)
    driver_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    vehicle_no = models.CharField(max_length=20)
    password = models.CharField(max_length=100)
    total_earnings = models.FloatField(default=0.0)
    accepting_rides = models.BooleanField(default=True)
    ride_ongoing = models.BooleanField(default=False)
    gender = models.CharField(max_length=10)
    profile_pic = models.CharField(max_length=100)
    chats = models.JSONField(default=list)  # List of chat IDs
    
    def __str__(self):
        return self.driver_name """


class all_rides(models.Model):
    ride_id = models.CharField(max_length=8, default=generate_random_id, primary_key=True)
    female_only =models.BooleanField(default=False)
    start = models.CharField(max_length=100)
    end = models.CharField(max_length=100) 
    vehicle_no = models.CharField(max_length=20, default=generate_random_id)
    shared =models.BooleanField(default=False)
    total_distance = models.FloatField(default=0)
    total_cost = models.FloatField(default=0)
    passenger_count = models.IntegerField(default=0)
    passengers = models.JSONField(default=dict) 

    def __str__(self):
        return f"Ride {self.ride_id} from {self.start} to {self.end}"
