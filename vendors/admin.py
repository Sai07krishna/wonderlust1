from django.contrib import admin
from .models import *
# Register your models here.
@admin.action(description='Mark selected packages as Approved')
def approve_packages(modeladmin, request, queryset):
    queryset.update(status='approved')

@admin.action(description='Mark selected packages as Rejected')
def reject_packages(modeladmin, request, queryset):
    queryset.update(status='rejected')

class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'price', 'status', 'vendor')
    list_filter = ('status', 'vendor')
    search_fields = ('name', 'destination', 'vendor__company_name')
    actions = [approve_packages, reject_packages]
    list_editable = ('status',)


admin.site.register(Registeredvendor)
admin.site.register(Package)
admin.site.register(PackageImage)