from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home.html', views.home, name='home'),
    path('chatroom/', views.chatroom, name='chatroom'),
    # path('chatroom/<int:group_id>/', views.chatroom, name='chatroom_with_group'),
    # path('create_group/', views.create_group, name='create_group'),
    
    # path('chatroom/<int:group_id>/', views.chatroom, name='chatroom_with_group'),
    # path('PreviousRides.html', views.previous_rides, name='previous_rides'),

    path('chatroom/', views.chatroom, name='chatroom'),
    path('chatroom/<int:group_id>/', views.chatroom, name='chatroom_with_group'),
    path('create_group/', views.create_group, name='create_group'),
    path('profile.html', views.profile, name='profile'),
    path('registration/', views.registration, name='registration'),
    path('login/', views.login, name='login'),
    path('create_ride/', views.create_ride, name='create_ride'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
    path('calculate_fare/', views.calculate_fare, name='calculate_fare'),
    path('previous_rides/',views.previous_rides,name='previous_rides'),
    path('chatroom/', views.chatroom, name='chatroom'),
    path('pin_board/<str:group_id>/', views.pin_board, name='pin_board'),



]
