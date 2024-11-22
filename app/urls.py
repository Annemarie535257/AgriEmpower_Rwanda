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

    # Dashboards
    path('dashboard/farmer/', views.farmer_dashboard, name='farmer_dashboard'),
    path('dashboard/cooperative/', views.cooperative_dashboard, name='cooperative_dashboard'),
    path('dashboard/financial-institution/', views.financial_institution_dashboard, name='financial_institution_dashboard'),

    # Loan Application Paths
    path('loan/apply/', views.apply_for_loan, name='apply_for_loan'),  # Apply for loan
    path('loan/apply/cooperative/', views.apply_for_loan_cooperative, name='apply_for_loan_cooperative'),
    # path('update-loan-status/<uuid:loan_id>/', views.update_loan_status, name='update_loan_status'),
    path('update-loan-status/<uuid:application_id>/', views.update_loan_status, name='update_loan_status'),
    path('update-cooperative-loan-status/<uuid:application_id>/', views.update_cooperative_loan_status, name='update_cooperative_loan_status'),

    # Loan Approval/Denial Paths for Cooperative Managers and Financial Institutions
    path('loan/approve/<uuid:loan_id>/', views.respond_to_loan_application, name='respond_to_loan_application'),  # Approve loan
    path('loan/reject/<uuid:loan_id>/', views.respond_to_loan_application, name='respond_to_loan_application'),  # Reject loan

    path('logout/', views.logout_view, name='logout'),


]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)