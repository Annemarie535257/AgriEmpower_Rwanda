from django import forms
from django.contrib.auth.models import User
from .models import Farmer, Cooperative, FinancialInstitution

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'password']


class FarmerRegistrationForm(forms.ModelForm):
    class Meta:
        model = Farmer
        fields = ['full_name', 'phone_number', 'farm_location', 'crop_types', 'farm_size']

class CooperativeRegistrationForm(forms.ModelForm):
    class Meta:
        model = Cooperative
        fields = ['name', 'phone_number', 'location', 'registration_number', 'number_of_members', 'performance_status']

class FinancialInstitutionRegistrationForm(forms.ModelForm):
    class Meta:
        model = FinancialInstitution
        fields = ['name', 'institution_type', 'phone_number', 'license_number', 'address', 'interest_rate_range']

# class FarmerProfileForm(forms.ModelForm):
#     class Meta:
#         model = FarmerProfile
#         fields = ['full_name', 'phone_number', 'farm_name', 'farm_location', 'farm_size', 'crop_type']
