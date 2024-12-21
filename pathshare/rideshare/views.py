from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
import requests
import polyline
import geopy.distance
import googlemaps
import math
from .models import Customer, all_rides
from django.http import HttpResponse, JsonResponse


def index(request):
    return render(request, 'index.html')
def chatroom(request):
    return render(request, 'chatroom.html')

def previous_rides(request):
    return render(request, 'PreviousRides.html')

from django.shortcuts import render, redirect
from .models import Customer

def profile(request):
    customer_id = request.session.get('customer_id')

    if not customer_id:
        return redirect('login')
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        request.session.flush()
        return redirect('login')

    return render(request, 'profile.html', {
        'customer': customer
    })


def home(request):
    return render(request, 'home.html')


def registration(request):
    if request.method == 'POST':
        name = request.POST.get('reg-name')
        email = request.POST.get('reg-email')
        number = request.POST.get('reg-phone')
        gender = request.POST.get('reg-gender')
        pic = request.POST.get('reg-pic')
        password = request.POST.get('reg-password')

        customer = Customer(
                customer_name=name,
                email=email,
                phone_number=number,
                gender=gender,
                profile_pic=pic,
                password=password
            )
        customer.save()
            
    return render(request, 'index.html', {})


def login(request):
    if request.method == "POST":
        name = request.POST.get('name')
        password = request.POST.get('password')

        try:
            customer = Customer.objects.get(customer_name=name)

            if customer.password == password:
                request.session['customer_id'] = customer.customer_id 
                request.session['customer_name'] = customer.customer_name  
                return render(request, 'home.html', {'customer_name': customer.customer_name})
            else:
                return render(request, 'index.html', {'alert_message': 'Incorrect Password!'})
        except Customer.DoesNotExist:
            return render(request, 'index.html', {'alert_message': 'User does not exist!'})
 
    return render(request, 'index.html', {})

def logout(request):
    request.session.flush() 
    return redirect('login') 

def get_coordinates(location, api_key):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": location, "key": api_key}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            coordinates = data['results'][0]['geometry']['location']
            return (coordinates['lat'], coordinates['lng'])
    return None

def get_route_polyline(start_location, end_location, api_key):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {"origin": start_location, "destination": end_location, "key": api_key}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'routes' in data and len(data['routes']) > 0:
            polyline_encoded = data['routes'][0]['overview_polyline']['points']
            return polyline.decode(polyline_encoded)
    return None

def is_point_on_route(start_location, end_location, point_location1, point_location2, api_key):
    start_coords = get_coordinates(start_location, api_key)
    end_coords = get_coordinates(end_location, api_key)
    point_coords1 = get_coordinates(point_location1, api_key)
    point_coords2 = get_coordinates(point_location2, api_key)

    if not start_coords or not end_coords or not point_coords1 or not point_coords2:
        return False
    polyline_points = get_route_polyline(start_location, end_location, api_key)
    if polyline_points is None:
        return False

    threshold = 500  
    for i in range(len(polyline_points) - 1):
        segment_start = polyline_points[i]
        segment_end = polyline_points[i + 1]

        if (is_point_near_segment(segment_start, segment_end, point_coords1, threshold) or
            is_point_near_segment(segment_start, segment_end, point_coords2, threshold)):
            return True

    return False

def is_point_near_segment(segment_start, segment_end, point, threshold):
    start_lat, start_lon = segment_start
    end_lat, end_lon = segment_end
    point_lat, point_lon = point

    start_lat, start_lon = map(math.radians, [start_lat, start_lon])
    end_lat, end_lon = map(math.radians, [end_lat, end_lon])
    point_lat, point_lon = map(math.radians, [point_lat, point_lon])

    segment_vector_x = end_lon - start_lon
    segment_vector_y = end_lat - start_lat
    point_vector_x = point_lon - start_lon
    point_vector_y = point_lat - start_lat

    cross_product = point_vector_x * segment_vector_y - point_vector_y * segment_vector_x
    segment_length = geopy.distance.great_circle(segment_start, segment_end).meters
    distance_to_segment = abs(cross_product) / segment_length

    return distance_to_segment < threshold




def create_ride(request):
    api_key = "yourAPIkey"  
    gmaps = googlemaps.Client(key=api_key)

    if request.method == "POST":
        female_only = request.POST.get("female_only") == 'true'
        source = request.POST.get("start_location")
        destination = request.POST.get("end_location")
        shared = 'shared' in request.POST
        
        directions = gmaps.directions(source, destination, mode="driving", units="metric")
        distance = directions[0]['legs'][0]['distance']['value'] / 1000  
        cost = math.ceil(distance * 25) 
    
    if shared and female_only and request.session.get('Gender')!='F':
        return redirect('home')
    elif shared:
        rides = all_rides.objects.all()
        
        for ride in rides:
            if is_point_on_route(ride.start, ride.end, source, destination, api_key) and \
               ((female_only and ride.female_only) or (not female_only and not ride.female_only)) and \
               ride.passenger_count < 4: 
                passengers = {
                    f"Passenger{ride.passenger_count + 1}": {
                        "customer_id" : request.session.get('customer_id'),
                        "Source": source.split(",")[0], 
                        "Destination": destination.split(",")[0],  
                        "Distance": distance,
                        "Cost": 0 
                    }
                }

                ride.passengers = {**ride.passengers, **passengers}  
                ride.passenger_count += 1
                ride.save()  
                return redirect('previous_rides')

        ridetemp = all_rides(
            female_only=female_only,
            start=source,
            end=destination,
            shared=shared,
            total_distance=distance,
            total_cost=cost,
            passenger_count=1,
            passengers={
                "Passenger1": {
                    "customer_id" : request.session.get('customer_id'),
                    "Source": source.split(",")[0],
                    "Destination": destination.split(",")[0],
                    "Distance": distance,
                    "Cost": 0
                }
            }
        )
        ridetemp.save()

    else:
        ridetemp = all_rides(
            female_only=female_only,
            start=source,
            end=destination,
            shared=shared,
            total_distance=distance,
            total_cost=cost,
            passenger_count=1,
            passengers={
                "Passenger1": {
                    "customer_id" : request.session.get('customer_id'),
                    "Source": source.split(",")[0],
                    "Destination": destination.split(",")[0],
                    "Distance": distance,
                    "Cost": 0
                }
            }
        )
        ridetemp.save()
        
    return redirect('previous_rides')

def calculate_fare(request):
    rides = all_rides.objects.all()
    for ride in rides:
        adaptive_fare_splitting(ride)
    return redirect('home') 

def adaptive_fare_splitting(ride):
    total_distance = sum(
        passenger_details["Distance"]
        for passenger_key, passenger_details in ride.passengers.items()
    )

    for passenger_key, passenger_details in ride.passengers.items():
        passenger_distance = passenger_details["Distance"]
        proportional_cost = math.ceil((passenger_distance / total_distance) * ride.total_cost)
        passenger_details["Cost"] = proportional_cost

    ride.save()

