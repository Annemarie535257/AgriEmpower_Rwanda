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
    path('signup/farmer/', views.signup_farmer, name='signup_farmer'),
    path('signup/cooperative/', views.signup_cooperative, name='signup_cooperative'),
    path('signup/financial-institution/', views.signup_financial_institution, name='signup_financial_institution'),

    # OTP Paths for Two-Factor Authentication
    path('verify-token/farmer/<str:username>/', views.verify_token_farmer, name='verify_token_farmer'),
    path('verify-token/cooperative/<str:username>/', views.verify_token_cooperative, name='verify_token_cooperative'),
    path('verify-token/financial-institution/<str:username>/', views.verify_token_financial_institution, name='verify_token_financial_institution'),
    # Authentication Path
    path('signin/farmer/', views.signin_farmer, name='signin_farmer'),
    path('signin/cooperative/', views.signin_cooperative, name='signin_cooperative'),
    path('signin/financial-institution/', views.signin_financial_institution, name='signin_financial_institution'),

    # Loan Application Paths
    path('loan/apply/', views.apply_for_loan, name='apply_for_loan'),  # Apply for loan
    path('loan/track/<uuid:loan_id>/', views.track_loan_status, name='track_loan_status'),  # Track loan status by loan ID

    # Loan Approval/Denial Paths for Cooperative Managers and Financial Institutions
    path('loan/approve/<uuid:loan_id>/', views.respond_to_loan_application, name='respond_to_loan_application'),  # Approve loan
    path('loan/reject/<uuid:loan_id>/', views.respond_to_loan_application, name='respond_to_loan_application'),  # Reject loan


]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
