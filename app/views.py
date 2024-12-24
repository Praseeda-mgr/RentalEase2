from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from .models import Property, Booking,Contact
from .forms import PropertyForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.paginator import Paginator

def registration(request):
    if not request.user.is_authenticated:

        if request.method == "POST":
            username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            password = request.POST.get('password')

            # Validation checks
            if not username or not first_name or not last_name or not email or not password:
                messages.error(request, 'Please fill in all the required fields')
                return redirect('register')

            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists. Please choose a different one')
                return redirect('register')

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists")
                return redirect('register')

            # Create the user
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password
            )

            # Authenticate and log the user in
            user = authenticate(request, username=username, password=password)
            if user is not None:
                print("Authentication successful.")
                login(request, user)
                messages.success(request, 'Registration successful. You are now logged in.')
                return redirect('home')
            else:
                print("Authentication failed.")
                messages.error(request, 'Authentication failed. Please try again.')
                return redirect('register')


        return render(request, 'registration.html')
    else:
        return redirect('home')



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
            user = User.objects.filter(email=email)
           
            if user.count() == 1:   
                user = user.first()
            elif user.count() > 1:
    # Handle duplicate emails
                error="Multiple accounts found with this email. Please contact support."
                return redirect('login')
            else:
              error="No account found with this email."
              return redirect('login')

            # print(user.email)
        except User.DoesNotExist:
            messages.error(request,"User does not exist") 
            return render(request, 'login.html')

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

def home_page(request):  
    property=Property.objects.all()
    search=request.GET.get('search')
    if search:
        property=property.filter(title__icontains=search)
    
    from_ = request.GET.get('from')
    to_ = request.GET.get('to')
    location = request.GET.get('location')
    
    if from_ and to_:
        property = property.filter(price__gte=from_, price__lt=to_)
    elif from_:
        property = property.filter(price__gte=from_)
    elif to_:
        property = property.filter(price__lt=to_)
    if location:
        property = property.filter(location__icontains=location)
    paginator = Paginator(property, 4)  # Show 4 properties per page
    page_number = request.GET.get('page')  # Get the page number from URL
    page_obj = paginator.get_page(page_number)  # Get the corresponding page object
    context={
        'property':property,
        'page_obj':page_obj
    }
    return render(request,'home.html',context)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
@login_required
def seller_dashboard(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        seller_id = request.user.id
        properties = Property.objects.filter(seller=request.user)
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
            return redirect('home')  # Redirect to avoid resubmission on page refresh
    else:
        form = PropertyForm()
    return render(request, 'add_property.html', {'form': form})


from django.shortcuts import get_object_or_404, redirect, render
from .forms import PropertyForm
from .models import Property


@login_required
def update_property(request, slug):
    # Get the property instance by ID
    property = Property.objects.get(slug=slug)

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
        'form': form,
        'property':property
    }
    return render(request, 'update_property.html', context)

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Property

@login_required

def delete_property(request, slug):
    message=""
    # Get the property instance by ID and ensure it belongs to the current user
    property = get_object_or_404(Property, slug=slug, seller=request.user)
    if request.method == "POST":
        # Delete the property
        property.delete()
        message="Property  deleted successfully"
        return redirect('allproperties')  # Redirect to the list of all properties

    context = {
        'property': property,
        message:""
    }
    return render(request, 'delete_property.html', context)

from django.shortcuts import get_object_or_404, redirect, render
from .models import Property, Booking
from django.contrib.auth.decorators import login_required

@login_required
def book_property(request, property_slug):
    
    property = get_object_or_404(Property,slug=property_slug)
    # booking = Booking.objects.get(id=1)
    # print(booking.property.slug)  # Outputs the slug of the associated property

    

    if request.method == 'POST':
        # Check if the property is approved and available
        if property.approval_status != 'rejected' and property.is_available and request.user!= property.seller:
            # Example booking creation logic
            booking = Booking.objects.create(
                property=property,
                client=request.user,
                approval_status='pending'
            )
            
            # Set the property as unavailable and booked
            property.is_available = False
            property.is_booked = True
            property.save()

            messages.success(request, "Booking request submitted successfully.")
            return redirect('home')  # Redirect to a success page or another URL
        else:
            messages.error(request,'THis is your property and you cannot book this property')

    return render(request, 'book_property.html', {'property': property})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Booking, Property
from django.contrib import messages

from django.contrib import messages

@login_required
def approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.property.seller != request.user:
        messages.error(
            request,
            f"You cannot approve the booking for {booking.property.title}.",
            extra_tags=f"property-{booking_id}"  # Custom tag for identifying this message
        )
        return redirect('bookings_list')

    # Approve booking
    booking.approval_status = 'approved'
    booking.property.is_booked = True
    booking.property.save()
    booking.save()

    messages.success(
        request,
        f"Booking for {booking.property.title} has been approved.",
        extra_tags=f"property -{booking_id}"  # Custom tag for identifying this message
    )
    return redirect('bookings_list')

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import Booking

@login_required
def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Check if the current user is the seller of the property
    if booking.property.seller != request.user:
        messages.error(request, "You are not authorized to reject this booking.", extra_tags=f"property-{booking_id}")
        return redirect('bookings_list')

    # Reject booking and update the property status
    booking.approval_status = 'rejected'
    booking.property.is_booked = False  # Ensure property is not marked as booked
    booking.property.save()
    booking.save()

    # Add success message
    messages.success(request, f"Booking for {booking.property.title} has been rejected.", extra_tags=f"booking-{booking_id}")
    
    # Redirect to the booking list
    return redirect('bookings_list')


@login_required
def property_detail(request, slug):
    property = get_object_or_404(Property,slug=slug)
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

# @login_required
# def book_property(request, property_slug):
#     # Ensure the property exists and is available
#     messages=""
#     property = get_object_or_404(Property, slug=property_slug, is_available=True)
#     booking = Booking.objects.filter(property=property).first()
#     if booking:
#         print(booking.property.slug)
#     else:
#         print("No booking found for this property.")

    

#     if request.method == 'POST':
#         # Check if the user already has a pending or confirmed booking for this property
#         if Booking.objects.filter(property=property, client=request.user, approval_status__in=['pending', 'confirmed']).exists():
#             messages="You already have an existing booking for this property."
#             return redirect('allproperties')

#         # Check if the property has any confirmed bookings by other users
#         if Booking.objects.filter(property=property, approval_status='confirmed').exists():
#             messages="This property is already fully booked."
#             return redirect('allproperties')

#         # Create a new booking request
#         booking = Booking(property=property, client=request.user, approval_status='pending')
#         booking.save()

#         messages="Your booking request has been submitted successfully!"
#         return redirect('allproperties')

#     return render(request, 'book_property.html', {'property': property,'messages':messages})


def Properties(request):
    property=Property.objects.filter(is_booked=False)
    paginator = Paginator(property, 4)  # Show 4 properties per page
    page_number = request.GET.get('page')  # Get the page number from URL
    page_obj = paginator.get_page(page_number)  # Get the corresponding page object
    context={
        'property':property,
        'page_obj':page_obj
    }
    return render(request,'property.html',context)

@login_required
def bookings_list(request):
    
    bookings = Booking.objects.filter(property__is_booked=False,approval_status='pending')

    # Handle approval and rejection
    action = request.GET.get('action')
    booking_id = request.GET.get('booking_id')

    if action and booking_id:
        booking = get_object_or_404(Booking, id=booking_id,approval_status='pending')

        if booking.property.seller != request.user:
            messages.error(request, "You are not authorized to perform this action.")
            return redirect('bookings_list')

        if action == 'approve':
            booking.approval_status = 'approved'
            booking.property.is_booked = True
            booking.property.save()
            booking.save()
            messages.success(request, f"Booking for {booking.property.title} has been approved.")
        elif action == 'reject':
            booking.approval_status = 'rejected'
            booking.property.is_booked = False
            booking.property.approval_status='rejected'
            booking.property.save()
            booking.save()
            messages.success(request, f"Booking for {booking.property.title} has been rejected.")

        return redirect('bookings_list')

    context = {'bookings': bookings}
    return render(request, 'booking_list.html', context)

  

@login_required
def contact_view(request):
    messages=""
    if request.method == 'POST':
        name = request.POST.get('name')
        
        phone_number = request.POST.get('phone_number')
       
        location = request.POST.get('location')
        
        email = request.POST.get('email')
        


        # Simple validation checks
        if not name or not phone_number or not location or not email:
            messages= "All fields are required."
        else:
            # Here you could save the data to the database or send an email, etc.
              Contact.objects.create(
                name=name,
                phone_number=phone_number,
                location=location,
                email=email
            )
              return redirect('allproperties')

    return render(request, 'contact.html',{'messages':messages})
@login_required
def admin_panel(request):
    if request.user.is_superuser:
        property=Property.objects.all()
        messages=Contact.objects.all()
    else:
        property=Property.objects.filter(seller=request.user)  
        messages=[]
    context={
        'property':property,
        'messages':messages
    }  
    return render(request, 'adminPanel.html',context)

def manageproperty(request):
    property=Property.objects.all()
    return render(request,'manageProperty.html',{'property':property})

def users(request):
    # Retrieve all properties
    properties = Property.objects.all()
    
    # Get distinct sellers who are associated with properties
    sellers = set(property.seller for property in properties if property.seller.is_authenticated)
    
    return render(request, 'seller.html', {'sellers': sellers})

def images(request):
    return render(request,'images.html')