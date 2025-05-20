from django.db import models

# Create your models here.

class Registeredvendor(models.Model):
    
    company_name = models.CharField(max_length=255)
    company_email = models.EmailField()
    company_phone = models.CharField(max_length=20)
    company_website = models.URLField(blank=True, null=True)
    business_type = models.CharField(max_length=100)
    years_in_business = models.PositiveIntegerField()
    business_description = models.TextField()
    business_documents = models.FileField(upload_to='vendor_documents/', blank=True, null=True)    
    admin_name = models.CharField(max_length=255)
    admin_email = models.EmailField()
    password = models.CharField(max_length=255)  
    agreed_terms = models.BooleanField(default=False)

class Package(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('private', 'Private'),
    ]

    vendor = models.ForeignKey(Registeredvendor, on_delete=models.CASCADE,null=True)  
    name = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()
    group_size = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    expiry_date = models.DateField(null=True, blank=True)
    views_count = models.IntegerField(default=0)


class PackageImage(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='package_images/')


