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

from .models import Farmer, Cooperative, FinancialInstitution, OTP, LoanApplication
from .schemas import (
    farmer_register_schema,
    cooperative_register_schema,
    financial_institution_register_schema,
    loan_application_schema,
    signin_schema,
    signin_response_schema
)

def home_view(request):
    return render(request, 'index.html')

def select_view(request):
    return render(request, 'select.html')



# Helper function to generate OTP expiration time
def get_expiry_time():
    return timezone.now() + timezone.timedelta(minutes=10)

# Helper function to send OTP email
def send_otp_email(email, otp_code):
    subject = "Your OTP Code for AgriEmpower"
    message = f"Your OTP code is {otp_code}. This code will expire in 10 minutes."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

# Farmer Registration
@swagger_auto_schema(
    method='post',
    operation_description="Register a new Farmer",
    request_body=farmer_register_schema,
    responses={201: 'Farmer registered successfully', 400: 'Bad Request'}
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_farmer(request):
    try:
        data = request.data
        if User.objects.filter(email=data['email']).exists():
            return Response({"error": "Email already exists"}, status=400)

        user = User.objects.create_user(username=data['full_name'], password=data['password'], email=data['email'])
        Farmer.objects.create(
            farmer_id=uuid.uuid4(),
            full_name=data['full_name'],
            email=data['email'],
            password=data['password'],
            phone_number=data['phone_number'],
            farm_location=data['farm_location'],
            crop_types=data['crop_types'],
            farm_size=data.get('farm_size')
        )
        return Response({"message": "Farmer registered successfully"}, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=400)

# Cooperative Registration
@swagger_auto_schema(
    method='post',
    operation_description="Register a new Cooperative",
    request_body=cooperative_register_schema,
    responses={201: 'Cooperative registered successfully', 400: 'Bad Request'}
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_cooperative(request):
    try:
        data = request.data
        if User.objects.filter(email=data['email']).exists():
            return Response({"error": "Email already exists"}, status=400)

        user = User.objects.create_user(username=data['name'], password=data['password'], email=data['email'])
        Cooperative.objects.create(
            coop_id=uuid.uuid4(),
            name=data['name'],
            email=data['email'],
            password=data['password'],
            phone_number=data['phone_number'],
            location=data['location'],
            registration_number=data['registration_number'],
            number_of_members=data['number_of_members'],
            performance_status=data.get('performance_status')
        )
        return Response({"message": "Cooperative registered successfully"}, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=400)

# Financial Institution Registration
@swagger_auto_schema(
    method='post',
    operation_description="Register a new Financial Institution",
    request_body=financial_institution_register_schema,
    responses={201: 'Financial Institution registered successfully', 400: 'Bad Request'}
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_financial_institution(request):
    try:
        data = request.data
        if User.objects.filter(email=data['email']).exists():
            return Response({"error": "Email already exists"}, status=400)

        user = User.objects.create_user(username=data['name'], password=data['password'], email=data['email'])
        FinancialInstitution.objects.create(
            fin_id=uuid.uuid4(),
            name=data['name'],
            institution_type=data['institution_type'],
            email=data['email'],
            password=data['password'],
            phone_number=data['phone_number'],
            license_number=data['license_number'],
            address=data['address'],
            interest_rate_range=data.get('interest_rate_range')
        )
        return Response({"message": "Financial Institution registered successfully"}, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=400)

# Request OTP
@swagger_auto_schema(
    method='post',
    operation_description="Request OTP for verification",
    responses={200: 'OTP sent to email', 400: 'Bad Request'}
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def request_otp(request):
    try:
        data = request.data
        email = data.get('email')
        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)

        otp_code = str(random.randint(100000, 999999))
        OTP.objects.update_or_create(
            email=email,
            defaults={'otp': otp_code, 'is_verified': False, 'expires_at': get_expiry_time()}
        )
        
        # Return the OTP code in the response for easier testing
        return JsonResponse({"message": "OTP generated successfully", "otp_code": otp_code}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# Verify OTP
@swagger_auto_schema(
    method='post',
    operation_description="Verify OTP",
    responses={200: 'OTP verified successfully', 400: 'Invalid or expired OTP'}
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    try:
        data = request.data
        # email = data.get('email')
        otp_code = data.get('otp')

        otp = OTP.objects.filter(otp=otp_code, is_verified=False).first()
        if otp and timezone.now() < otp.expires_at:
            otp.is_verified = True
            otp.save()
            return JsonResponse({"message": "OTP verified successfully"}, status=200)

        return JsonResponse({"error": "Invalid or expired OTP"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

#signin

@swagger_auto_schema(
    method='post',
    operation_description="Sign in to the application",
    request_body=signin_schema,
    responses={200: signin_response_schema, 400: 'Bad Request'}
)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def signin(request):
    try:
        data = request.data
        email = data.get('email')
        password = data.get('password')

        user = User.objects.filter(email=email).first()
        if user is None:
            return Response({"error": "User not found"}, status=400)

        if not user.check_password(password):
            return Response({"error": "Invalid password"}, status=400)

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "Login successful"
        })

    except Exception as e:
        return Response({"error": str(e)}, status=400)

# Loan Application
@swagger_auto_schema(
    method='post',
    operation_description="Apply for a loan",
    request_body=loan_application_schema,
    responses={201: 'Loan application submitted', 400: 'Bad Request'}
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def apply_for_loan(request):
    try:
        data = request.data
        farmer = Farmer.objects.get(farmer_id=data['farmer_id'])
        financial_institution = FinancialInstitution.objects.get(fin_id=data['financial_institution_id'])
        
        loan_application = LoanApplication.objects.create(
            farmer=farmer,
            financial_institution=financial_institution,
            loan_amount=data['loan_amount'],
            loan_status='Pending'
        )
        return Response({
            "message": "Loan application submitted",
            "loan_id": str(loan_application.loan_id),
            "farmer": loan_application.farmer.full_name,
            "financial_institution": loan_application.financial_institution.name,
            "loan_amount": loan_application.loan_amount,
            "loan_status": loan_application.loan_status
        }, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=400)

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
