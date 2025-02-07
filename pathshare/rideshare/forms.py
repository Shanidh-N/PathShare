# rideshare/forms.py
from django import forms
from .models import Customer

class CustomerRegistrationForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['customer_name', 'email', 'phone_number', 'password', 'gender', 'profile_pic']

""" class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['Name', 'Email', 'PhoneNumber', 'VehicleNumberPlate', 'Password', 'Gender', 'ProfilePic'] """

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
