from django.urls import path
from .import views as v


urlpatterns =[
                path('',v.index,name="home"),
                path('login/',v.usrlogin,name="userlogin"),
                path('signinuser/',v.usrsignin,name="usersignin"),
                path('userlogout/',v.usrlogout,name="userlogout"),
                path('profile/',v.profile,name="userprofile"),
                path('profilesettings/', v.profile_settings, name='profile_settings'),
                path('aboutus/',v.aboutus,name="aboutus"),
                path('contact/',v.contact,name="contact"),
                path('packages/', v.featured_packages, name='featured_packages'),
                path('packages/<int:package_id>/', v.viewdetails, name='viewdetails'),
                path('reviews/',v.reviews,name="reviews"),
                path('book/<int:package_id>/', v.book_package, name='book_package'),
                path('booking-confirmation/<int:booking_id>/', v.booking_confirmation, name='booking_confirmation'),
                path('payment-success/<int:booking_id>/', v.payment_success, name='payment_success'),
                path('my-bookings/', v.view_booked, name='view_booked'),
                path('booking/<int:booking_id>/', v.booking_detail, name='booking_detail'),


                
]