from django.urls import path
from .import views as v



urlpatterns=[
                 path('vendorsignin/',v.vendorregister,name="vendorsignin"),
                 path('vendorlogin/',v.vendorlogin,name="vendorlogin"),
                 path('vendordash/',v.vendordash,name="vendordash"),
                 path('vendor/addpackage/',v.add_package,name="add_package"),
                 path('vendorlogout/',v.vendorlogut,name="vendorlogout"),
                 path('pendingpackage/',v.pending_packages_view,name="pending_package"),
                 path('package_details/<int:package_id>/', v.package_details, name='package_details'),
                 path('package/update/<int:package_id>/', v.update_package, name='update_package'),
                 path('package/<int:pk>/make_private/', v.make_package_private, name='make_private'),
                 path('package/<int:pk>/delete/', v.delete_package, name='delete_package'),
                 path('package/<int:pk>/make_public/', v.make_package_public, name='make_public'),
                 path('vendor/bookings/', v.vendor_bookings, name='vendor_bookings'),
                 path('vendor/bookings/respond/<int:booking_id>/', v.respond_to_booking, name='respond_to_booking'),
                 path('terms/',v.terms,name="terms"),


             ]


