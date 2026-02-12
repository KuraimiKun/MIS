from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Bookings
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/create/', views.booking_create, name='booking_create'),
    path('bookings/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('bookings/<int:pk>/update-status/', views.booking_update_status, name='booking_update_status'),
    path('bookings/<int:booking_id>/payment/', views.add_payment, name='add_payment'),
    path('bookings/<int:booking_id>/penalty/', views.add_penalty, name='add_penalty'),
    path('bookings/<int:booking_id>/equipment/<int:equipment_id>/return/', views.return_equipment, name='return_equipment'),
    path('bookings/<int:booking_id>/receipt/', views.print_receipt, name='print_receipt'),
    
    # Court Schedule
    path('schedule/', views.court_schedule, name='court_schedule'),
    
    # Customers
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    
    # Equipment
    path('equipment/', views.equipment_list, name='equipment_list'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
    
    # API endpoints
    path('api/check-availability/', views.api_check_availability, name='api_check_availability'),
    path('api/court-price/', views.api_get_court_price, name='api_get_court_price'),
    path('api/search-customer/', views.api_search_customer, name='api_search_customer'),
]
