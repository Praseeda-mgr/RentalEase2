from django.db import models
from django.contrib.auth.models import User

class Property(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties',default=True) 
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    approval_status = models.CharField(
        max_length=10,
        choices=[('approved', 'Approved'), ('rejected', 'Rejected'), ('pending', 'Pending')],
        default='pending'
    )
    is_available = models.BooleanField(default=True)
    is_booked = models.BooleanField(default=False)
    image = models.ImageField(upload_to='property_images/', blank=True, null=True) 
    def __str__(self):
        return f'{self.title} - {self.id}'
    

class Booking(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    is_booked = models.BooleanField(default=False)
    approval_status = models.CharField(    # Added approval_status for booking requests
        max_length=10,
        choices=[('approved', 'Approved'), ('rejected', 'Rejected'), ('pending', 'Pending')],
        default='pending'
    )

    def __str__(self):
        return f'{self.property.seller} - {self.client.username}'
    
class Contact(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    location = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return f"{self.name} - {self.email}"
