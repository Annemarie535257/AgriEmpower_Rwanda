from django import forms
from django.contrib.auth.models import User
from .models import Farmer, Cooperative, FinancialInstitution, LoanApplication, LoanApplicationCooperative


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



class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = ['farmer', 'financial_institution', 'loan_pdf']

class LoanApplicationCooperativeForm(forms.ModelForm):
    class Meta:
        model = LoanApplicationCooperative
        fields = ['cooperative', 'financial_institution', 'loan_pdf']
