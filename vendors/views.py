from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from users.models import *
from .forms import *
from datetime import datetime
from django.db.models import F
from django.forms import modelformset_factory
from django.contrib import messages
from django.contrib.auth.hashers import make_password,check_password
from django.contrib.auth.decorators import login_required 
from django.core.files.storage import FileSystemStorage


# Create your views here.
def vendorregister(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        company_email = request.POST.get('company_email')
        company_phone = request.POST.get('company_phone')
        company_website = request.POST.get('company_website')
        business_type = request.POST.get('business_type')
        years_in_business = request.POST.get('years_in_business')
        business_description = request.POST.get('business_description')
        business_documents = request.FILES.get('business_documents')
        admin_name = request.POST.get('admin_name')
        admin_email = request.POST.get('admin_email')
        password = request.POST.get('password')
        agreed_terms = request.POST.get('agreed_terms') == 'on'

        hashed_password = make_password(password)

        vendor = Registeredvendor(
            company_name=company_name,
            company_email=company_email,
            company_phone=company_phone,
            company_website=company_website,
            business_type=business_type,
            years_in_business=years_in_business,
            business_description=business_description,
            business_documents=business_documents,
            admin_name=admin_name,
            admin_email=admin_email,
            password=hashed_password,
            agreed_terms=agreed_terms
        )
        vendor.save()

        messages.success(request, 'Vendor registered successfully!')
        return redirect('vendorlogin')
    
    return render(request,"vendors/vendorregister.html")



def vendorlogin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            vendor = Registeredvendor.objects.get(admin_email=email)
            if check_password(password, vendor.password): 
                request.session['vendor_id'] = vendor.id  
                return redirect('vendordash')
            else:
                messages.error(request, 'Incorrect password.')
        except Registeredvendor.DoesNotExist:
            messages.error(request, 'Vendor with this email does not exist.')


    return render(request,"vendors/vendorlogin.html")

def vendorlogut(request):
    def vendor_logout(request):
       if 'vendor_id' in request.session:
        del request.session['vendor_id']   
        messages.success(request, 'You have been logged out successfully.')
    return redirect('vendorlogin')  

def vendordash(request):
    vendor_id = request.session.get('vendor_id')
    if not vendor_id:
        messages.error(request, "Please login first.")
        return redirect('vendorlogin')

    total_packages = Package.objects.filter(vendor_id=vendor_id).count()
    pending_packages = Package.objects.filter(vendor_id=vendor_id, status='pending').count()
    approved_packages = Package.objects.filter(vendor_id=vendor_id, status='approved').count()
    active_packages = Package.objects.filter(status='approved', vendor_id=vendor_id)


    return render(request, "vendors/vendordash.html", {
        "total_packages": total_packages,
        "pending_packages": pending_packages,
        "active_bookings": approved_packages, 
        "active_packages": active_packages,
    })



def add_package(request):
    if request.method == 'POST':
        name = request.POST.get('package_name')
        destination = request.POST.get('destination')
        price = request.POST.get('price')
        duration = request.POST.get('duration')
        group_size = request.POST.get('group_size')
        description = request.POST.get('description')
        expiry_date_str = request.POST.get('expiry_date')
        images = request.FILES.getlist('images')

        vendor_id = request.session.get('vendor_id')
        if not vendor_id:
            messages.error(request, "Vendor not logged in.")
            return redirect('vendorlogin')

        vendor = Registeredvendor.objects.get(id=vendor_id)

        expiry_date = None
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "Invalid expiry date format.")
                return redirect('vendordash')

        package = Package.objects.create(
            name=name,
            destination=destination,
            price=price,
            duration=duration,
            group_size=group_size,
            description=description,
            status='pending',
            vendor=vendor,
            expiry_date=expiry_date
        )

        for img in images:
            fs = FileSystemStorage()
            filename = fs.save(img.name, img)
            PackageImage.objects.create(package=package, image=filename)

        return redirect('vendordash')

    return redirect('vendordash')


def pending_packages_view(request):
    vendor_id = request.session.get('vendor_id')
    if not vendor_id:
        messages.error(request, "Please login first.")
        return redirect('vendorlogin')

    pending_packages = Package.objects.filter(status='pending', vendor_id=vendor_id)

    return render(request, "vendors/pendingpackage.html", {
        "pending_packages": pending_packages,
        "pending_count": pending_packages.count()
    })


def approve_package(request, package_id):
    if not request.user.is_staff:  
        messages.error(request, "You are not authorized to approve packages.")
        return redirect('pending_packages')

    package = get_object_or_404(Package, id=package_id)
    package.status = 'approved'
    package.save()
    messages.success(request, f"Package '{package.package_name}' approved successfully.")
    return redirect('pending_packages')

def reject_package(request, package_id):
    if not request.user.is_staff:  
        messages.error(request, "You are not authorized to reject packages.")
        return redirect('pending_packages')

    package = get_object_or_404(Package, id=package_id)
    package.status = 'rejected'
    package.save()
    messages.success(request, f"Package '{package.package_name}' rejected successfully.")
    return redirect('pending_packages')

def package_details(request, package_id):
    package = get_object_or_404(Package, id=package_id)

    
    Package.objects.filter(id=package_id).update(views_count=F('views_count') + 1)

    booking_count = Booking.objects.filter(package=package).count()

    
    recent_bookings = Booking.objects.filter(package=package).select_related('user').order_by('-created_at')[:5]

    return render(request, "vendors/package_detail.html", {
        'package': package,
        'booking_count': booking_count,
        'recent_bookings': recent_bookings,
    })



def update_package(request, package_id):
    package = get_object_or_404(Package, id=package_id)

    PackageImageFormSet = modelformset_factory(
        PackageImage,
        fields=('image',),
        extra=3,
        can_delete=True
    )

    if request.method == 'POST':
        form = PackageForm(request.POST, request.FILES, instance=package)
        formset = PackageImageFormSet(
            request.POST,
            request.FILES,
            queryset=PackageImage.objects.filter(package=package),
            prefix='images'
        )

        if form.is_valid() and formset.is_valid():
            package = form.save()  

            
            instances = formset.save(commit=False)
            for instance in instances:
                instance.package = package
                instance.save()

            
            for obj in formset.deleted_objects:
                obj.image.delete(save=False)  
                obj.delete()

            return redirect('package_details', package_id=package.id)

        else:
            print("Form errors:", form.errors)
            print("Formset errors:", formset.errors)

    else:
        form = PackageForm(instance=package)
        formset = PackageImageFormSet(
            queryset=PackageImage.objects.filter(package=package),
            prefix='images'
        )

    return render(request, 'vendors/update_package.html', {
        'form': form,
        'formset': formset,
        'package': package
    })


def vendor_bookings(request):
    vendor_id = request.session.get('vendor_id')
    if not vendor_id:
        return redirect('vendorlogin') 

    vendor = Registeredvendor.objects.get(id=vendor_id)
    vendor_packages = Package.objects.filter(vendor=vendor)
    bookings = Booking.objects.filter(package__in=vendor_packages)
    return render(request, 'vendors/vendor_bookings.html', {'bookings': bookings})

def respond_to_booking(request, booking_id):
    vendor_id = request.session.get('vendor_id')
    if not vendor_id:
        return redirect('vendorlogin')

    vendor = Registeredvendor.objects.get(id=vendor_id)
    booking = get_object_or_404(Booking, id=booking_id, package__vendor=vendor)

    if request.method == 'POST':
        status = request.POST.get('status')  
        message = request.POST.get('message')
        booking.vendor_status = status
        booking.vendor_message = message
        booking.save()
        return redirect('vendor_bookings')

    return render(request, 'vendors/respond_booking.html', {'booking': booking})




def make_package_private(request, pk):
    package = get_object_or_404(Package, pk=pk)
    package.status = 'private'
    package.save()
    return redirect('package_details', package_id=pk)

def make_package_public(request, pk):
    package = get_object_or_404(Package, pk=pk)
    package.status = 'approved'
    package.save()
    return redirect('package_details', package_id=pk)  


def delete_package(request, pk):
    package = get_object_or_404(Package, pk=pk)
    package.delete()
    return redirect('vendordash')  

def terms(request):
    return render(request,'vendors/terms.html')
