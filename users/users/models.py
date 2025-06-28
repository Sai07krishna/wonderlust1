from django.db import models
from django.utils import timezone
from vendors.models import Package



# Create your models here.

class RegisteredUser(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    dob = models.DateField()
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    preferences = models.JSONField(default=list)
    budget = models.CharField(max_length=50)


class  Contactsmessage(models.Model):
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    email=models.EmailField()
    phone=models.CharField(max_length=15)
    subject=models.CharField(max_length=100)
    message=models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)


class Reviews(models.Model):
    name=models.CharField(max_length=20)
    review=models.TextField()
    rating=models.IntegerField()
    date=models.DateField(auto_now_add=True)

class Booking(models.Model):
    user = models.ForeignKey(RegisteredUser, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    travel_date = models.DateField()
    travelers = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    payment_status = models.CharField(max_length=50, default='Pending')

    
    vendor_status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected'),
        ],
        default='Pending'
    )
    vendor_message = models.TextField(blank=True, null=True)


