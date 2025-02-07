from django.db import models
import random
import string
from django.contrib.auth.models import User
import uuid
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
        return self.email



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


    
class Ride(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='rides')  # Add related_name
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    distance = models.FloatField()
    cost = models.FloatField()
    female_only = models.BooleanField(default=False)
    shared = models.BooleanField(default=False)
    ride_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ride from {self.start_location} to {self.end_location}"




from django.contrib.auth.models import User
import uuid



class Groups(models.Model):
    group_id = models.CharField(max_length=8, default=generate_random_id, primary_key=True)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    day_of_journey = models.CharField(max_length=50)
    time_of_journey = models.TimeField()
    female_only=models.BooleanField(default=False)
    member_count = models.IntegerField(default=0) 
    members = models.ManyToManyField(Customer, related_name="groups")
    created_by=models.CharField(max_length=50, default = 0)

    def new_member(self, customer):
        if self.female_only and customer.gender.lower() != "female":
            raise ValueError("Only Female members can join this group.")

        if customer.customer_id in self.members:
            raise ValueError("You are already a member of this group.")

        if self.member_count < 4:
            self.members.append(customer.customer_id)
            self.member_count += 1
            self.save()
            return True

        if self.member_count >= 4:
            return False
    def __str__(self):
        return f"{self.source} - {self.destination}"



class Message(models.Model):
    group = models.ForeignKey(Groups, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(Customer, on_delete=models.CASCADE)
    text = models.CharField(
        max_length=255,
        choices=[
            ("NOT_COMING", "Not coming"),
            ("LATE_5", "Late by 5 min"),
            ("LATE_10", "Late by 10 min"),
            ("READY", "Ready to go"),
        ],
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.get_text_display()}"



##############################
# chat pin post and club room creation

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