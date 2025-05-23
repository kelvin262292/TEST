from django import forms
from .models import Address

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'phone_number', 'street_address', 'city', 'state_or_province', 'postal_code', 'country']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'placeholder': 'e.g. John Doe'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'placeholder': 'e.g. 0900123456'}),
            'street_address': forms.TextInput(attrs={'class': 'form-input w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'placeholder': 'e.g. 123 Nguyen Hue St, District 1'}),
            'city': forms.TextInput(attrs={'class': 'form-input w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'placeholder': 'e.g. Ho Chi Minh City'}),
            'state_or_province': forms.TextInput(attrs={'class': 'form-input w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'placeholder': 'e.g. Ho Chi Minh City'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-input w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'placeholder': 'e.g. 700000'}),
            'country': forms.TextInput(attrs={'class': 'form-input w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'}),
        }
        labels = {
            'full_name': 'Full Name',
            'phone_number': 'Phone Number',
            'street_address': 'Street Address',
            'city': 'City',
            'state_or_province': 'State/Province',
            'postal_code': 'Postal Code',
            'country': 'Country',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].initial = 'Vietnam' # Set default value for country
        # You can add more custom validation if needed
        self.fields['full_name'].required = True
        self.fields['phone_number'].required = True
        self.fields['street_address'].required = True
        self.fields['city'].required = True
        self.fields['state_or_province'].required = True
        self.fields['postal_code'].required = True
        self.fields['country'].required = True

from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User # Corrected: Use the User model directly
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'placeholder': 'e.g. John'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'placeholder': 'e.g. Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-input w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'placeholder': 'e.g. john.doe@example.com'}),
        }
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email Address',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        # Email uniqueness will be handled by default User model validation if changed
