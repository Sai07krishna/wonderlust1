from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password,check_password
from django.contrib.auth.decorators import login_required
import razorpay
import re
from django.conf import settings
from .models import *
from .forms import *
from vendors.models import Package
from datetime import date


# Create your views here.
def index(request):
    featured_packages = Package.objects.filter(status='approved')[:3]  
    return render(request, "index.html", {"featured_packages": featured_packages})


def usrlogin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            user = RegisteredUser.objects.get(email=email)
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                request.session['user_name'] = f"{user.first_name} {user.last_name}"
                messages.success(request, 'Login successful.')
                return redirect('home')
            else:
                messages.error(request, 'Incorrect password.')
                return render(request, "users/login.html")  
        except RegisteredUser.DoesNotExist:
            messages.error(request, 'Email not found.')
            return render(request, "users/login.html")  
    
    return render(request, "users/login.html")  

def usrlogout(request):
    request.session.flush()  
    messages.success(request, "You have been logged out.")
    return redirect('userlogin')  




def usrsignin(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        dob = request.POST.get('dob')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        preferences = request.POST.getlist('preferences[]')  
        budget = request.POST.get('budget')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('user_register')

        
        hashed_password = make_password(password)

       
        RegisteredUser.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            dob=dob,
            email=email,
            password=hashed_password,
            preferences=preferences,
            budget=budget
        )

        messages.success(request, "Registration successful! Please log in.")
        return redirect('userlogin')

    else:
          return render(request, "users/userregister.html")



def profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('userlogin')

    bookings = Booking.objects.filter(user_id=user_id).select_related('package').order_by('-created_at')
    today = date.today()
    upcoming_count = bookings.filter(travel_date__gte=today).count()
    completed_count = bookings.filter(travel_date__lt=today).count()

    return render(request, "users/profile.html", {
        'bookings': bookings,
        'upcoming_count': upcoming_count,
        'completed_count': completed_count
    })


def profile_settings(request):
    user_id = request.session.get('user_id')  
    if not user_id:
        return redirect('login')  

    user = get_object_or_404(RegisteredUser, id=user_id)
    form = RegisteredUserForm(instance=user)

    if request.method == 'POST':
        form = RegisteredUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile_settings')

    return render(request, 'users/settingsuser.html', {'form': form})


def aboutus(request):
    return render(request,"users/aboutus.html")


def contact(request):
    if request.method=="POST":
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        phone=request.POST.get('phone')
        subject=request.POST.get('subject')
        message=request.POST.get('message')

        cont=Contactsmessage(first_name=first_name,last_name=last_name,email=email,phone=phone,subject=subject,message=message)
        cont.save()

        return redirect('home')
    else:

      return render(request,"users/contact.html")
    
def featured_packages(request):
    packages = Package.objects.filter(status='approved').prefetch_related('images')

    
    duration = request.GET.get('duration')
    price = request.GET.get('price')

    
    if duration:
        try:
            packages = packages.filter(duration__lte=int(duration))
        except ValueError:
            pass

    
    if price == '1':
        packages = packages.filter(price__gte=10000, price__lte=25000)
    elif price == '2':
        packages = packages.filter(price__gt=25000, price__lte=50000)
    elif price == '3':
        packages = packages.filter(price__gt=50000)

    return render(request, 'users/featured_package.html', {
        'packages': packages,
        'selected_duration': duration,
        'selected_price': price,
    })

def viewdetails(request, package_id):
    package = get_object_or_404(Package, id=package_id)
    images = package.images.all()  # related_name from PackageImage model
    similar_packages = Package.objects.exclude(id=package_id)[:3]
    return render(request, 'users/viewpackage.html', {
        'package': package,
        'images': images,
        'similar_packages': similar_packages
    })

@login_required
def reviews(request):
    if request.method == "POST":
        name = request.POST.get("name")
        review = request.POST.get("review")
        rating = request.POST.get("rating")

        if name and review and rating:
            Reviews.objects.create(name=name, review=review, rating=int(rating))

    review_list = Reviews.objects.all().order_by('-date')
    return render(request, "users/userreview.html", {"reviews": review_list})


def book_package(request, package_id):
    package = get_object_or_404(Package, id=package_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)

            
            user_id = request.session.get('user_id')
            if not user_id:
                messages.error(request, "You must be logged in to book a package.")
                return redirect('userlogin')

            user = RegisteredUser.objects.get(id=user_id)

            booking.user = user
            booking.package = package
            booking.total_price = package.price * form.cleaned_data['travelers']
            booking.save()

            
            return redirect('booking_confirmation', booking_id=booking.id)
    else:
        form = BookingForm()

    return render(request, 'users/book_package.html', {
        'package': package,
        'form': form
    })

def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount = int(booking.total_price * 100)

    razorpay_order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"
    })

    booking.razorpay_order_id = razorpay_order['id']
    booking.save()

    context = {
        "booking": booking,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": razorpay_order['id'],
        "amount": amount,
    }

    return render(request, 'users/booking_confirmation.html', context)

def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.payment_status = 'Paid'
    booking.save()

    return render(request, 'users/payment_success.html', {'booking': booking})

def view_booked(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('userlogin')

    user = RegisteredUser.objects.get(id=user_id)
    bookings = Booking.objects.filter(user=user).select_related('package').order_by('-created_at')
    return render(request, 'users/view_booked.html', {'bookings': bookings})

def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'users/booking_detail.html', {'booking': booking})