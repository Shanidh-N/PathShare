from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
import requests
import polyline
import geopy.distance
import googlemaps
import math
from .models import *
from django.http import HttpResponse, JsonResponse,HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib import messages
def index(request):
    return render(request, 'index.html')


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
                print("Session ID after login:", request.session.get('customer_id'))  # Debugging session data
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
    api_key = 'AIzaSyBxoe1p0VmnCiU90-CRs8Y3veMKwBo1R0o'
    gmaps = googlemaps.Client(key=api_key)

    if request.method == "POST":
        female_only = request.POST.get("female_only") == 'true'
        source = request.POST.get("start_location")
        destination = request.POST.get("end_location")
        shared = 'shared' in request.POST

        # Get the route information from Google Maps API
        directions = gmaps.directions(source, destination, mode="driving", units="metric")
        distance = directions[0]['legs'][0]['distance']['value'] / 1000  # Convert from meters to kilometers
        cost = math.ceil(distance * 25)  # Example cost calculation based on distance

        customer_id = request.session.get('customer_id')
        if not customer_id:
            return redirect('login')  # Ensure user is logged in

        # If shared and female-only, ensure the gender is correct
        if shared and female_only and request.session.get('Gender') != 'F':
            return redirect('home')

        elif shared:
            # Check for an existing shared ride that fits the criteria
            rides = all_rides.objects.all()
            for ride in rides:
                if is_point_on_route(ride.start, ride.end, source, destination, api_key) and \
                   ((female_only and ride.female_only) or (not female_only and not ride.female_only)) and \
                   ride.passenger_count < 4:
                    
                    # Check if the customer is already in this ride
                    if customer_id in ride.passengers:
                        break  # Customer is already part of the ride, don't add again

                    # Add the new passenger to the ride
                    ride.passengers[customer_id] = {
                        "Source": source.split(",")[0],
                        "Destination": destination.split(",")[0],
                        "Distance": distance,
                        "Cost": 0  # Cost for this passenger
                    }
                    ride.passenger_count += 1
                    ride.save()

                    # Add the ride to the customer's previous rides using the Ride model
                    customer = Customer.objects.get(customer_id=customer_id)
                    passenger_data = ride.passengers[customer_id]

                    # Create a new Ride record for the customer and save it
                    ride_instance = Ride(
                        customer=customer,
                        start_location=passenger_data['Source'],
                        end_location=passenger_data['Destination'],
                        distance=passenger_data['Distance'],
                        cost=passenger_data['Cost'],
                        female_only=female_only,
                        shared=shared
                    )
                    ride_instance.save()  # Save the ride record to the database

                    return redirect('previous_rides')

            # If no shared ride was found or customer was already in a ride, create a new ride
            ridetemp = all_rides(
                female_only=female_only,
                start=source,
                end=destination,
                shared=shared,
                total_distance=distance,
                total_cost=cost,
                passenger_count=1,
                passengers={
                    customer_id: {
                        "Source": source.split(",")[0],
                        "Destination": destination.split(",")[0],
                        "Distance": distance,
                        "Cost": 0
                    }
                }
            )
            ridetemp.save()

        else:
            # If it's not a shared ride, just create a single-passenger ride
            ridetemp = all_rides(
                female_only=female_only,
                start=source,
                end=destination,
                shared=shared,
                total_distance=distance,
                total_cost=cost,
                passenger_count=1,
                passengers={
                    customer_id: {
                        "Source": source.split(",")[0],
                        "Destination": destination.split(",")[0],
                        "Distance": distance,
                        "Cost": 0
                    }
                }
            )
            ridetemp.save()

        # Add the new ride to the customer's previous rides using the Ride model
        customer = Customer.objects.get(customer_id=customer_id)
        passenger_data = ridetemp.passengers[customer_id]

        # Create a new Ride record for the customer and save it
        ride_instance = Ride(
            customer=customer,
            start_location=passenger_data['Source'],
            end_location=passenger_data['Destination'],
            distance=passenger_data['Distance'],
            cost=passenger_data['Cost'],
            female_only=female_only,
            shared=shared
        )
        ride_instance.save()  # Save the ride record to the database

    return redirect('previous_rides')


def calculate_fare(request):
    rides = all_rides.objects.all()
    for ride in rides:
        adaptive_fare_splitting(ride)
    return redirect('previous_rides') 

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

from django.shortcuts import render, redirect
from .models import Ride, Customer, all_rides

def previous_rides(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')
    
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return redirect('login')

    all_rides_for_user = all_rides.objects.all()
    current_ride_details = None  # Initialize to avoid UnboundLocalError

    for ride in all_rides_for_user:
        if customer_id in ride.passengers:
            passenger_data = ride.passengers[customer_id]
            current_ride_details = {
                "ride_id": ride.ride_id,
                "source": passenger_data["Source"],
                "destination": passenger_data["Destination"],
                "distance": passenger_data["Distance"],
                "cost": passenger_data["Cost"],
                "female_only": ride.female_only,
                "shared": ride.shared
            }
            
            # Check if the ride_id is already in previous_rides
            ride_found = False
            for prev_ride in customer.previous_rides:
                if prev_ride["ride_id"] == ride.ride_id:
                    # If found, update the cost (and any other fields if needed)
                    prev_ride["cost"] = current_ride_details["cost"]
                    ride_found = True
                    continue
            
            # If the ride_id is not found, append the new ride
            if not ride_found:
                customer.previous_rides.append(current_ride_details)
            
            customer.save()
          # Exit the loop after processing the first matching ride

    previous_rides = customer.previous_rides  # Get all the previous rides

    context = {
        'current_ride': current_ride_details,
        'previous_rides': previous_rides,
    }
    
    return render(request, 'PreviousRides.html', context)



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Groups, Customer, Message

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def create_group(request):
    if request.method == "POST":
        customer_id = request.session.get("customer_id")  # Get customer ID from session
        if not customer_id:
            return redirect("login")  # Redirect if not in session

        customer = Customer.objects.get(customer_id=customer_id)  # Fetch customer

        source = request.POST.get("source")
        destination = request.POST.get("destination")
        day_of_journey = request.POST.get("day_of_journey")
        time_of_journey = request.POST.get("time_of_journey")
        female_only = request.POST.get("female_only") == "on"

        # Create the group
        group = Groups.objects.create(
            source=source,
            destination=destination,
            day_of_journey=day_of_journey,
            time_of_journey=time_of_journey,
            female_only=female_only,
            created_by=customer  # Associate with the session customer
        )

        # Add the customer to the members list of the group
        group.members.add(customer.customer_id)  # Add customer ID to the members list
        group.member_count += 1  # Increment the member count
        group.save()  # Save the group after modification

        return redirect("chatroom")

    return HttpResponseForbidden("403 Forbidden - Invalid request method")

def chatroom(request, group_id=None):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect("login")  # Redirect to login if customer is not logged in

    customer = Customer.objects.get(customer_id=customer_id)

    if group_id:
        # Handle group-specific view
        group = Groups.objects.get(id=group_id)

        # Check if the customer is a member of the group
        if customer.customer_id not in group.members:
            return redirect('chatroom')  # Redirect to chatroom if customer isn't a member

        messages = group.messages.all()
        return render(request, 'chatroom_group.html', {'group': group, 'messages': messages, 'customer': customer})

    # Get the groups where the customer is a member
    groups = Groups.objects.filter(members__in=[customer.customer_id])  # Change contains to in

    return render(request, 'chatroom.html', {'groups': groups, 'customer': customer})




def pin_board(request, group_id):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect("login")

    customer = Customer.objects.get(customer_id=customer_id)
    group = get_object_or_404(Groups, id=group_id)

    # Check if the customer is a member
    if customer not in group.members.all():
        messages.error(request, "You are not a member of this group.")
        return redirect("chatroom")

    if request.method == "POST":
        selected_message = request.POST.get("message")
        if selected_message:
            Message.objects.create(group=group, sender=customer, text=selected_message)
            messages.success(request, "Message sent!")

    group_messages = Message.objects.filter(group=group).order_by("-timestamp")

    return render(request, "pin_board.html", {"group": group, "messages": group_messages, "customer": customer})
