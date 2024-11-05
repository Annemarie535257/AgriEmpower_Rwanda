from django.shortcuts import render
from django.contrib import admin
from django.urls import path
from . import views  # Make sure to import views from your app
from django.conf import settings
from django.conf.urls.static import static

def homepage(request):
    # print("Home view called")
    return render(request, 'index.html')


urlpatterns = [
    

    # Registration Paths
    path('', homepage, name='homepage'),  # Homepage
    path('home/', views.home_view, name='home'),  # Homepage
    path('select/', views.select_view, name='select'),  
    path('register/farmer/', views.register_farmer, name='register_farmer'),
    path('register/cooperative/', views.register_cooperative, name='register_cooperative'),
    path('register/financial_institution/', views.register_financial_institution, name='register_financial_institution'),

    # OTP Paths for Two-Factor Authentication
    path('otp/request/', views.request_otp, name='request_otp'),
    path('otp/verify/', views.verify_otp, name='verify_otp'),

    # Authentication Path
    path('signin/', views.signin, name='signin'),

    # Loan Application Paths
    path('loan/apply/', views.apply_for_loan, name='apply_for_loan'),  # Apply for loan
    path('loan/track/<uuid:loan_id>/', views.track_loan_status, name='track_loan_status'),  # Track loan status by loan ID

    # Loan Approval/Denial Paths for Cooperative Managers and Financial Institutions
    path('loan/approve/<uuid:loan_id>/', views.respond_to_loan_application, name='respond_to_loan_application'),  # Approve loan
    path('loan/reject/<uuid:loan_id>/', views.respond_to_loan_application, name='respond_to_loan_application'),  # Reject loan


]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
