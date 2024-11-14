import logging
logger = logging.getLogger(__name__)

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
import json
import random
import uuid
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import redirect
from .forms import UserRegistrationForm, FarmerRegistrationForm, CooperativeRegistrationForm, FinancialInstitutionRegistrationForm
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest


from .models import Farmer, Cooperative, FinancialInstitution, OTP, LoanApplication
from .schemas import (
    farmer_register_schema,
    cooperative_register_schema,
    financial_institution_register_schema,
    loan_application_schema,
    signin_schema,
    signin_response_schema
)
from django.contrib.auth import logout


def home_view(request):
    return render(request, 'index.html')

def select_view(request):
    return render(request, 'select.html')

def cooperative_dashboard(request):
    return render(request, 'cooperative_dashboard.html')

def farmer_dashboard(request):
    # Assuming the user is already authenticated, fetch the farmer profile from the user
    farmer = get_object_or_404(Farmer, user=request.user)
    
    # Proceed with rendering the dashboard or handling other logic
    return render(request, 'farmer_dashboard.html', {'farmer': farmer})
def financial_institution_dashboard(request):
    return render(request, 'institution_dashboard.html')

# Helper function to generate OTP expiration time
def get_expiry_time():
    return timezone.now() + timezone.timedelta(minutes=10)

# Helper function to send OTP email
def send_otp_email(email, otp_code):
    subject = "Your OTP Code for AgriEmpower"
    message = f"Your OTP code is {otp_code}. This code will expire in 10 minutes."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

# view for the registration of the farmer

def signup_farmer(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        farmer_form = FarmerRegistrationForm(request.POST)

        if user_form.is_valid() and farmer_form.is_valid():
            # Create user but don't save to database yet
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data.get('password'))  # Set password
            user.is_active = False  # Set user as inactive until OTP is verified
            user.username = farmer_form.cleaned_data.get('full_name')  # Set username as full name
            user.save()

            # Create Farmer instance linked to user
            # farmer = farmer_form.save(commit=False)
            # farmer.user = user  # Assuming you have a OneToOne relationship with User
            # farmer.save()

            # Create Farmer instance linked to user
            farmer = Farmer.objects.create(
                user=user,
                full_name=farmer_form.cleaned_data.get('full_name'),
                email=user.email,
                password=user.password,  # Store the password hash
                phone_number=farmer_form.cleaned_data.get('phone_number'),
                farm_location=farmer_form.cleaned_data.get('farm_location'),
                crop_types=farmer_form.cleaned_data.get('crop_types', ''),
                farm_size=farmer_form.cleaned_data.get('farm_size', None),
                farm_name=farmer_form.cleaned_data.get('farm_name', '')
            )
            farmer.save()


            # Generate OTP
            otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            otp_expiration = timezone.now() + timezone.timedelta(minutes=5)
            OTP.objects.create(
                email=user.email,
                otp=otp_code,
                expires_at=otp_expiration
            )

            # Send OTP via email
            subject = "Email Verification - AgriEmpower Rwanda"
            message = f"Hi {user.username}, here is your OTP: {otp_code}. It expires in 5 minutes."
            sender = "amtwagirayezu@gmail.com"  # Replace with your email
            receiver = [user.email]
            send_mail(subject, message, sender, receiver, fail_silently=False)

            messages.success(request, "Account created successfully! An OTP was sent to your email.")
            return redirect("verify_token_farmer", username=user.username)

    else:
        user_form = UserRegistrationForm()
        farmer_form = FarmerRegistrationForm()

    context = {"user_form": user_form, "farmer_form": farmer_form}
    return render(request, "registerf.html", context)

# Cooperative Registration
def signup_cooperative(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        cooperative_form = CooperativeRegistrationForm(request.POST)

        if user_form.is_valid() and cooperative_form.is_valid():
            # Create user but don't save to database yet
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data.get('password'))  # Set password
            user.is_active = False  # Set user as inactive until OTP is verified
            user.username = cooperative_form.cleaned_data.get('name')  # Set username as cooperative name
            user.save()

            # Create Cooperative instance linked to user
            cooperative = cooperative_form.save(commit=False)
            cooperative.user = user  # Assuming you have a OneToOne relationship with User
            # cooperative.coop_id = uuid.uuid4()  # Generate unique cooperative ID
            cooperative.save()

            # Generate OTP
            otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            otp_expiration = timezone.now() + timezone.timedelta(minutes=5)
            OTP.objects.create(
                email=user.email,
                otp=otp_code,
                expires_at=otp_expiration
            )

            # Send OTP via email
            subject = "Email Verification - AgriEmpower Rwanda"
            message = f"Hi {user.username}, here is your OTP: {otp_code}. It expires in 5 minutes."
            sender = "your_email@example.com"  # Replace with your email
            receiver = [user.email]
            send_mail(subject, message, sender, receiver, fail_silently=False)

            messages.success(request, "Account created successfully! An OTP was sent to your email.")
            return redirect("verify_token_cooperative", username=user.username)

    else:
        user_form = UserRegistrationForm()
        cooperative_form = CooperativeRegistrationForm()

    context = {"user_form": user_form, "cooperative_form": cooperative_form}
    return render(request, "registerc.html", context)

# Financial Institution Registration
def signup_financial_institution(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        financial_institution_form = FinancialInstitutionRegistrationForm(request.POST)

        if user_form.is_valid() and financial_institution_form.is_valid():
            # Create user but don't save to database yet
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data.get('password'))  # Set password
            user.is_active = False  # Set user as inactive until OTP is verified
            user.username = financial_institution_form.cleaned_data.get('name')  # Set username as financial institution name
            user.save()

            # Create Financial Institution instance linked to user
            financial_institution = financial_institution_form.save(commit=False)
            financial_institution.user = user  # Assuming you have a OneToOne relationship with User
            # financial_institution.fin_id = uuid.uuid4()  # Generate unique financial institution ID
            financial_institution.save()

            # Generate OTP
            otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            otp_expiration = timezone.now() + timezone.timedelta(minutes=5)
            OTP.objects.create(
                email=user.email,
                otp=otp_code,
                expires_at=otp_expiration
            )

            # Send OTP via email
            subject = "Email Verification - AgriEmpower Rwanda"
            message = f"Hi {user.username}, here is your OTP: {otp_code}. It expires in 5 minutes."
            sender = "your_email@example.com"  # Replace with your email
            receiver = [user.email]
            send_mail(subject, message, sender, receiver, fail_silently=False)

            messages.success(request, "Account created successfully! An OTP was sent to your email.")
            return redirect("verify_token_financial_institution", username=user.username)

    else:
        user_form = UserRegistrationForm()
        financial_institution_form = FinancialInstitutionRegistrationForm()

    context = {"user_form": user_form, "financial_institution_form": financial_institution_form}
    return render(request, "registerfin.html", context)

# vrify token for the farmer
def verify_token_farmer(request, username):
    user = get_object_or_404(User, username=username)
    user_otp = OTP.objects.filter(email=user.email).last()

    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')  # OTP entered by the user
        if otp_code and user_otp and user_otp.otp == otp_code:
            if user_otp.expires_at > timezone.now():
                user.is_active = True
                user.save()
                messages.success(request, "Account activated successfully! You can now log in.")
                return redirect("signin_farmer")  # Change to your farmer login URL
            else:
                messages.warning(request, "The OTP has expired, please request a new OTP.")
                return redirect("verify_token_farmer", username=user.username)
        else:
            messages.warning(request, "Invalid OTP entered, please try again.")
            return redirect("verify_token_farmer", username=user.username)

    context = {'user': user}
    return render(request, "otp_f.html", context)

# vrify token for the cooperative

def verify_token_cooperative(request, username):
    user = get_object_or_404(User, username=username)
    user_otp = OTP.objects.filter(email=user.email).last()

    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')  # Make sure this matches your form field name
        logger.info(f"OTP entered by user: {otp_code}, OTP from DB: {user_otp.otp if user_otp else 'None'}")

        if otp_code and user_otp and user_otp.otp == otp_code:
            if user_otp.expires_at > timezone.now():
                user.is_active = True
                user.save()
                messages.success(request, "Account activated successfully! You can now log in.")
                return redirect("signin_cooperative")  # Redirect to cooperative login page
            else:
                messages.warning(request, "The OTP has expired, please request a new OTP.")
        else:
            messages.warning(request, "Invalid OTP entered, please try again.")

        return redirect("verify_token_cooperative", username=user.username)

    context = {'user': user}
    return render(request, "otp_c.html", context)

def verify_token_financial_institution(request, username):
    user = get_object_or_404(User, username=username)
    user_otp = OTP.objects.filter(email=user.email).last()

    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')  # OTP entered by the user
        if otp_code and user_otp and user_otp.otp == otp_code:
            if user_otp.expires_at > timezone.now():
                user.is_active = True
                user.save()
                messages.success(request, "Account activated successfully! You can now log in.")
                return redirect("signin_financial_institution")  # Change to your financial institution login URL
            else:
                messages.warning(request, "The OTP has expired, please request a new OTP.")
                return redirect("verify_token_financial_institution", username=user.username)
        else:
            messages.warning(request, "Invalid OTP entered, please try again.")
            return redirect("verify_token_financial_institution", username=user.username)

    context = {'user': user}
    return render(request, "otp_fin.html", context)

#signin view for the farmer

def signin_farmer(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            username = User.objects.get(email=email).username
        except User.DoesNotExist:
            messages.warning(request, "Invalid email or password.")
            return redirect("signin_farmer")
        
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_active:
                login(request, user)
                messages.success(request, f"Hi {user.username}, you are now logged in.")
                return redirect("farmer_dashboard")  # Redirect to your farmer dashboard URL
           
        else:
            messages.warning(request, "Invalid credentials or account is not active.")
            return redirect("signin_farmer")

    return render(request, "loginf.html", {"form": None})

#signin view for the cooperative

def signin_cooperative(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            username = User.objects.get(email=email).username
        except User.DoesNotExist:
            messages.warning(request, "Invalid email or password.")
            return redirect("signin_cooperative")
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None or user.is_active:
                    
                    login(request, user)
                    messages.success(request, f"Hi {user.username}, you are now logged in.")
                    return redirect("cooperative_dashboard")  # Redirect to your cooperative dashboard URL
               
        else:
            messages.warning(request, "Invalid credentials or account is not active.")
            return redirect("signin_cooperative")

    return render(request, "loginc.html", {"form": None})



#signin view for the financial institution

def signin_financial_institution(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            username = User.objects.get(email=email).username
        except User.DoesNotExist:
            messages.warning(request, "Invalid email or password.")
            return redirect("signin_financial_institution")
        
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_active:

                login(request, user)
                messages.success(request, f"Hi {user.username}, you are now logged in.")
                return redirect("financial_institution_dashboard")  # Redirect to your financial institution dashboard URL
            
        else:
            messages.warning(request, "Invalid credentials or account is not active.")
            return redirect("sign_financial_institution")

    return render(request, "loginfin.html", {"form": None})

def apply_for_loan(request):
    if request.method == 'POST':
        farmer_id = request.POST.get('farmer_id')
        financial_institution = request.POST.get('financial_institution')
        loan_form = request.FILES.get('loan_form')

        if not farmer_id or not financial_institution or not loan_form:
            messages.error(request, "All fields are required.")
            return redirect('farmer_dashboard')

        try:
            # Get the farmer using farmer_id
            farmer = Farmer.objects.get(farmer_id=farmer_id)

            # Assuming FinancialInstitution has a unique name
            financial_institution_obj = FinancialInstitution.objects.get(name=financial_institution)

            # Create a loan application
            loan_application = LoanApplication.objects.create(
                farmer=farmer,
                financial_institution=financial_institution_obj,
                loan_amount=5000,  # or capture this value from the form if needed
                loan_status='Pending',
                form_file=loan_form  # assuming LoanApplication model has a FileField for form_file
            )

            # Redirect back to farmer dashboard with a success query parameter
            return redirect('farmer_dashboard') + '?loan_submitted=true'

        except Farmer.DoesNotExist:
            messages.error(request, "Farmer not found.")
            return redirect('farmer_dashboard')

        except FinancialInstitution.DoesNotExist:
            messages.error(request, "Selected financial institution not found.")
            return redirect('farmer_dashboard')

    messages.error(request, "Invalid request method.")
    return redirect('farmer_dashboard')

# Loan Application Response (Approve or Deny)
@swagger_auto_schema(
    method='post',
    operation_description="Respond to a loan application (Approve or Deny)",
    responses={200: 'Loan status updated', 404: 'Loan application not found', 400: 'Bad Request'}
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def respond_to_loan_application(request, loan_id):
    try:
        data = request.data
        loan_application = LoanApplication.objects.get(loan_id=loan_id)
        action = data.get('action')

        if action not in ['approve', 'deny']:
            return Response({"error": "Invalid action. Must be 'approve' or 'deny'."}, status=400)

        if action == 'approve':
            loan_application.loan_status = 'Approved'
            message = "Loan approved"
        elif action == 'deny':
            loan_application.loan_status = 'Denied'
            message = "Loan denied"

        loan_application.save()
        return Response({
            "message": message,
            "loan_id": str(loan_application.loan_id),
            "loan_status": loan_application.loan_status
        }, status=200)

    except LoanApplication.DoesNotExist:
        return Response({"error": "Loan application not found"}, status=404)

    except Exception as e:
        return Response({"error": str(e)}, status=400)
    
# Track Loan Status
@swagger_auto_schema(
    method='get',
    operation_description="Track loan status by loan ID",
    responses={200: 'Loan status retrieved', 404: 'Loan application not found'}
)
@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def track_loan_status(request, loan_id):
    try:
        loan_application = LoanApplication.objects.get(loan_id=loan_id)
        return Response({
            "loan_id": str(loan_application.loan_id),
            "farmer": loan_application.farmer.full_name,
            "financial_institution": loan_application.financial_institution.name,
            "loan_amount": loan_application.loan_amount,
            "loan_status": loan_application.loan_status
        }, status=200)

    except LoanApplication.DoesNotExist:
        return Response({"error": "Loan application not found"}, status=404)

# Logout View
def logout_view(request):
    try:
        # Log out the current user
        logout(request)
        messages.success(request, "You have been successfully logged out.")
        # Redirect to the homepage or login page after logout
        return redirect('homepage')  # Assuming you have a home view
    except Exception as e:
        logger.error(f"Error occurred during logout: {str(e)}")
        messages.error(request, "An error occurred during logout. Please try again later.")
        return redirect('homepage')

