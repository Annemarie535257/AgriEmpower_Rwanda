from django.contrib import admin
from .models import Farmer, Cooperative, FinancialInstitution, LoanApplication, OTP, LoanApplicationCooperative
from django.utils.html import format_html

@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ('farmer_id','full_name', 'email', 'phone_number', 'farm_location', 'farm_size')
    search_fields = ('full_name', 'email', 'phone_number')
    list_filter = ('farm_location',)

@admin.register(Cooperative)
class CooperativeAdmin(admin.ModelAdmin):
    list_display = ('coop_id','name', 'email', 'location', 'registration_number', 'number_of_members', 'performance_status')
    search_fields = ('name', 'registration_number')
    list_filter = ('location', 'performance_status')

@admin.register(FinancialInstitution)
class FinancialInstitutionAdmin(admin.ModelAdmin):
    list_display = ('fin_id','name', 'institution_type', 'email', 'phone_number', 'license_number', 'address', 'interest_rate_range')
    search_fields = ('name', 'institution_type', 'email', 'phone_number')
    list_filter = ('institution_type',)

@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'farmer', 'financial_institution','loan_pdf', 'loan_status', 'submission_date')
    search_fields = ('loan_id', 'farmer__full_name', 'financial_institution__name')
    list_filter = ('loan_status', 'submission_date')

    def loan_pdf(self, obj):
        if obj.loan_pdf:
            return format_html('<a href="{}">Download pdf</a>', obj.loan_pdf.url)
        return 'No pdf'
    
@admin.register(LoanApplicationCooperative)
class LoanApplicationCooperativeAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'cooperative', 'financial_institution','loan_pdf', 'loan_status', 'submission_date')
    search_fields = ('loan_id', 'cooperative__name', 'financial_institution__name')
    list_filter = ('loan_status', 'submission_date')

    def loan_pdf(self, obj):
        if obj.loan_pdf:
            return format_html('<a href="{}">Download pdf</a>', obj.loan_pdf.url)
        return 'No pdf'


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp', 'is_verified', 'created_at', 'expires_at')
    search_fields = ('email',)
    list_filter = ('is_verified',)
