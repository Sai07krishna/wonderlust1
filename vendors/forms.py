from django import forms
from django.forms import inlineformset_factory
from .models import Package, PackageImage

class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ['name', 'destination', 'price', 'duration', 'group_size', 'description','expiry_date']

PackageImageFormSet = inlineformset_factory(
    Package,
    PackageImage,
    fields=['image'],
    extra=3,
    can_delete=True
)
