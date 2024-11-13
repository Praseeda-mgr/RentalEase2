from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from .models import Property, Booking
from .forms import PropertyForm


def registration(request):
    error = None
    if request.method == "POST":
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            error = "Username already exists"
        else:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)
            return redirect('login')
    context = {
        'error': error
    }
    return render(request, 'registration.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

def login_page(request):
    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Ensure user exists before attempting password verification
        try:
            user = User.objects.get(email=email)
            print(user.email)
        except User.DoesNotExist:
            error = "User does not exist"
            return render(request, 'login.html', {'error': error})

        # Verify the password manually
        if check_password(password, user.password):
            login(request, user)
            return redirect('home')  # Redirect to the desired page after login
        else:
            error = "Your email or password is incorrect"

    context = {
        'error': error
    }
    return render(request, 'login.html', context)



def logout_page(request):
    if request.user.is_authenticated:
        logout(request)  
    return redirect('login')  

def index(request):
    return render(request, 'index.html')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
@login_required
def home_page(request):  
    return render(request, 'home.html')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
@login_required
def seller_dashboard(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        seller_id = request.user.id
        properties = Property.objects.all()
        # Define context with all necessary data
        context = {
            'seller_id': seller_id,
            'properties': properties
        }
        # Use the defined context in the render function
        return render(request, 'seller_dashboard.html', context)
    else:
        # Redirect to login page if the user is not authenticated
        return redirect('login')

    
from django.shortcuts import render, redirect
from .forms import PropertyForm
from .models import Property

@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)  # Include request.FILES for image upload
        if form.is_valid():
            property = form.save(commit=False)
            property.seller = request.user
            # Set availability based on checkbox
            is_available = request.POST.get('is_available')
            property.is_available = True if is_available == "on" else False
            property.save()
            return redirect('allproperties')  # Redirect to avoid resubmission on page refresh
    else:
        form = PropertyForm()
    return render(request, 'add_property.html', {'form': form})


from django.shortcuts import get_object_or_404, redirect, render
from .forms import PropertyForm
from .models import Property


@login_required
def update_property(request, id):
    # Get the property instance by ID
    property = Property.objects.get(id=id)

    if request.method == "POST":
        # Bind form with POST data and instance to update
        form = PropertyForm(request.POST, instance=property)
        if form.is_valid():
            updated_property = form.save(commit=False)
            
            # Set the seller to the current user (ensuring it's a User instance)
            updated_property.seller = request.user
            
            # Update availability based on checkbox
            is_available = request.POST.get('is_available')
            updated_property.is_available = True if is_available == "on" else False
            
            # Save the updated property instance
            updated_property.save()
            return redirect('allproperties')  # Redirect to the seller dashboard
            
    else:
        form = PropertyForm(instance=property)
    
    context = {
        'form': form
    }
    return render(request, 'update_property.html', context)

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Property

@login_required
def delete_property(request, id):
    # Get the property instance by ID and ensure it belongs to the current user
    property = get_object_or_404(Property, id=id, seller=request.user)
    if request.method == "POST":
        # Delete the property
        property.delete()
        messages.success(request, 'Property deleted successfully.')
        return redirect('allproperties')  # Redirect to the list of all properties

    context = {
        'property': property
    }
    return render(request, 'confirm_delete.html', context)

from django.shortcuts import get_object_or_404, redirect, render
from .models import Property, Booking
from django.contrib.auth.decorators import login_required

@login_required
def book_property(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    property_image = property.image  # Get the property image

    if request.method == 'POST':
        # Check if the property is approved and available
        if property.approval_status == 'approved' and property.is_available:
            # Example booking creation logic
            booking = Booking.objects.create(
                property=property,
                user=request.user,
                status='pending'
            )
            
            # Set the property as unavailable and booked
            property.is_available = False
            property.is_booked = True
            property.save()

            messages.success(request, 'Booking request submitted successfully.')
            return redirect('allproperties')  # Redirect to a success page or another URL
        else:
            messages.error(request, 'This property is either not approved or not available for booking.')

    return render(request, 'book_property.html', {'property': property})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Booking, Property
from django.contrib import messages

@login_required
def approve_booking(request, id):
    # Fetch the booking object, ensure it's not already booked
    booking = get_object_or_404(Booking, id=id)
    property = booking.property

    # Check if the property is already booked
    if property.is_booked:
        messages.error(request, "This property is already booked.")
        return redirect('/property')

    if request.method == "POST":
        approval_status = request.POST.get("status")
        
        # Check if the selected approval_status is valid
        if approval_status in ["approved", "rejected"]:
            booking.approval_status = approval_status
            
            if approval_status == "approved":
                property.is_booked = True
                property.save()  # Mark the property as booked

            booking.save()  # Save the booking status
            messages.success(request, f"The booking has been {approval_status} successfully.")
            return redirect('/property')
        else:
            messages.error(request, "Invalid status selected.")

    return render(request, 'booking_approve.html', {'booking': booking})

@login_required
def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, property__seller=request.user)
    
    # Reject the booking
    booking.approval_status = 'rejected'
    booking.save()
    return redirect('/property')  # Redirect to seller's booking list


@login_required
def property_detail(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    booking = None

    # Check if the user has a booking for this property
    if request.user.is_authenticated:
        booking = Booking.objects.filter(property=property, client=request.user).first()

    # Determine availability based on the booking status
    is_available = property.is_available and (booking is None or booking.approval_status != 'approved')

    context = {
        'property': property,
        'booking': booking,
        'is_available': is_available,
    }
    return render(request, 'property_details.html', context)


@login_required
def seller_bookings(request):
    
    properties = Property.objects.filter(seller=request.user)
    
    # Retrieve all bookings related to these properties
    bookings = Booking.objects.filter(property__in=properties)

    context = {
        'bookings': bookings,
    }
    return render(request, 'seller_bookings.html', context)


@login_required
def update_booking_status(request, booking_id, status):
    booking = get_object_or_404(Booking, id=booking_id, property__seller=request.user)
    if status in ['approved', 'rejected']:
        booking.approval_status = status
        booking.save()
    return redirect('seller_bookings')

@login_required
def book_property(request, property_id):
    # Ensure the property exists and is available
    property = get_object_or_404(Property, id=property_id, is_available=True)

    if request.method == 'POST':
        # Check if the user already has a pending or confirmed booking for this property
        if Booking.objects.filter(property=property, client=request.user, approval_status__in=['pending', 'confirmed']).exists():
            messages.warning(request, "You already have an existing booking for this property.")
            return redirect('allproperties')

        # Check if the property has any confirmed bookings by other users
        if Booking.objects.filter(property=property, approval_status='confirmed').exists():
            messages.warning(request, "This property is already fully booked.")
            return redirect('allproperties')

        # Create a new booking request
        booking = Booking(property=property, client=request.user, approval_status='pending')
        booking.save()

        messages.success(request, "Your booking request has been submitted successfully!")
        return redirect('allproperties')

    return render(request, 'book_property.html', {'property': property})

@login_required
def Properties(request):
    property=Property.objects.filter(is_booked=False)
    context={
        'property':property
    }
    return render(request,'Property.html',context)

@login_required
def booking_list(request):
    # Fetch bookings that are not approved
    bookings = Booking.objects.filter(approval_status__in=['pending', 'rejected'])
    return render(request, 'booking_list.html', {'bookings': bookings})

@login_required
def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')
        location = request.POST.get('location')
        email = request.POST.get('email')

        # Simple validation checks
        if not name or not phone_number or not location or not email:
            messages.error(request, "All fields are required.")
        else:
            # Here you could save the data to the database or send an email, etc.
            return redirect('allproperties')

    return render(request, 'contact.html')