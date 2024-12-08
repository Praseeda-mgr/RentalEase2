
from django.urls import path
from app.views import *

urlpatterns = [
    path('index/', index, name='index'),
    path('register/',registration,name='register'),
    path('login/',login_page,name='login'),
    path('',home_page,name='home'),
    path('logout/',logout_page,name='logout'),
    path('seller_dashboard/', seller_dashboard, name='seller'),
    path('add',add_property,name='add_property'),
    path('delete/<int:id>/', delete_property, name='delete_property'),
    path('update/<int:id>/', update_property, name='update_property'),
    path('property', Properties, name='allproperties'),
    path('property/<int:property_id>/', property_detail, name='property_detail'),
      path('seller/bookings/', seller_bookings, name='seller_bookings'),
      path('seller/bookings/<int:booking_id>/<str:status>/', update_booking_status, name='update_booking_status'),
      path('property/<int:property_id>/book/', book_property, name='book_property'),
     path('adminpanel',admin_panel,name='adminPanel'),
     path('bookings', bookings_list, name='bookings_list'),

         path('approve_booking/<int:booking_id>/', approve_booking, name='approve_booking'),
    path('reject_booking/<int:booking_id>/', reject_booking, name='reject_booking'),
        path('contact', contact_view, name='contact'),
        path('manageproperty',manageproperty,name='manageproperty'),
        path('users',users,name='users'),

]