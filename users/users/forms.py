from django import forms
from .models import *

class RegisteredUserForm(forms.ModelForm):
    class Meta:
        model = RegisteredUser
        fields = ['first_name', 'last_name', 'phone', 'dob', 'email', 'preferences', 'budget']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'preferences': forms.Textarea(attrs={'rows': 3}),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['travel_date', 'travelers']
        widgets = {
            'travel_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'travelers': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
