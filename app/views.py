import logging
logger = logging.getLogger(__name__)
from django.http import HttpResponseRedirect
from django.urls import reverse
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
from django.contrib.auth import update_session_auth_hash
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
    try:
        cooperative = Cooperative.objects.get(user=request.user)
        loan_applications = LoanApplicationCooperative.objects.filter(cooperative=cooperative)
        print(f"Loan applications for cooperative {cooperative.name}: {loan_applications}")

        # Determine the current loan status if a loan exists
        current_loan_status = None
        if loan_applications.exists():
            current_loan_status = loan_applications.first().loan_status
            print(f"Current loan status: {current_loan_status}")
        else:
            print("No loan applications found for this cooperative.")

        return render(request, 'cooperative_dashboard.html', {
            'cooperative': cooperative,
            'loan_status': current_loan_status,
        })
    except Cooperative.DoesNotExist:
        print("Cooperative does not exist for the logged-in user.")
        return render(request, 'cooperative_dashboard.html', {'error': 'Cooperative not found.'})
    except Exception as e:
        print(f"Error in cooperative_dashboard: {e}")
        return render(request, 'cooperative_dashboard.html', {'error': str(e)})

# views.py
from django.shortcuts import render
from django.http import JsonResponse
from .models import Farmer, LoanApplication

def farmer_dashboard(request):
    try:
        # Fetch the logged-in farmer
        farmer = Farmer.objects.get(user=request.user)

        # Fetch the farmer's loan application
        loan_application = LoanApplication.objects.filter(farmer=farmer).first()  # Assuming one loan per farmer
        if loan_application:
            print(f"Loan found for farmer {farmer.full_name}: {loan_application.loan_status}")
        else:
            print(f"No loan found for farmer {farmer.full_name}")

        return render(request, 'farmer_dashboard.html', {
            'farmer': farmer,
            'application': loan_application,
            'application_id': loan_application.loan_id if loan_application else None
        })
    except Exception as e:
        print(f"Error in fetching farmer dashboard data: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def financial_institution_dashboard(request):
    # Get the logged-in user's financial institution (using the username as the institution name)
    financial_institution_name = request.user.username
    print(f"Logged-in User's Financial Institution: {financial_institution_name}")

    # Debug: List all registered users
    all_users = [user.username for user in User.objects.all()]
    print(f"All Registered Users: {all_users}")

    # Fetch the financial institution object associated with the logged-in user
    financial_institution_obj = get_object_or_404(FinancialInstitution, name__iexact=financial_institution_name)
    print(f"Financial Institution Object Fetched: {financial_institution_obj.name}")

    # Fetch loan applications submitted by farmers
    farmer_loan_applications = LoanApplication.objects.filter(financial_institution=financial_institution_obj)
    print(f"Number of Farmer Loan Applications Found: {farmer_loan_applications.count()}")

    # Fetch loan applications submitted by cooperatives
    cooperative_loan_applications = LoanApplicationCooperative.objects.filter(financial_institution=financial_institution_obj)
    print(f"Number of Cooperative Loan Applications Found: {cooperative_loan_applications.count()}")

    # Debug: Print details of farmer loan applications
    if farmer_loan_applications.exists():
        for application in farmer_loan_applications:
            print(f"Farmer Loan Application - Farmer: {application.farmer.full_name}, PDF: {application.loan_pdf.url if application.loan_pdf else 'No PDF'}")
    else:
        print("No farmer loan applications found.")

    # Debug: Print details of cooperative loan applications
    if cooperative_loan_applications.exists():
        for coop_application in cooperative_loan_applications:
            print(f"Cooperative Loan Application - Cooperative: {coop_application.cooperative.name}, PDF: {coop_application.loan_pdf.url if coop_application.loan_pdf else 'No PDF'}")
    else:
        print("No cooperative loan applications found.")

    # Context data for the template
    context = {
        'financial_institution': financial_institution_obj,
        'farmer_loan_applications': farmer_loan_applications,
        'cooperative_loan_applications': cooperative_loan_applications,
    }

    return render(request, 'institution_dashboard.html', context)


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
        # Check for duplicate username
        if User.objects.filter(username=request.POST.get('name')).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)

        # Check for duplicate email
        if User.objects.filter(email=request.POST.get('email')).exists():
            return JsonResponse({'error': 'Email already exists'}, status=400)

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
            return redirect("signin_financial_institution")

    return render(request, "loginfin.html", {"form": None})
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import LoanApplication, Farmer, FinancialInstitution, LoanApplicationCooperative

def apply_for_loan(request):
    if request.method == 'POST':
        print("Form submission started.")

        # Fetch form data
        farmer_id = request.POST.get('farmer_id')
        financial_institution = request.POST.get('financial_institution')
        loan_pdf = request.FILES.get('loan_pdf')

        # Print debug information
        print(f"Farmer ID: {farmer_id}")
        print(f"Financial Institution: {financial_institution}")
        print(f"Uploaded File: {loan_pdf}")

        # Check if file and fields are received
        if not farmer_id:
            print("Farmer ID is missing.")
            messages.error(request, "Farmer ID is required.")
            return redirect('farmer_dashboard')

        if not financial_institution:
            print("Financial Institution is missing.")
            messages.error(request, "Financial Institution is required.")
            return redirect('farmer_dashboard')

        if not loan_pdf:
            print("File upload failed: No file received.")
            messages.error(request, "Loan form (PDF) is required.")
            return redirect('farmer_dashboard')

        # Validate file type (optional but recommended)
        if not loan_pdf.name.endswith('.pdf'):
            print("Invalid file type.")
            messages.error(request, "Only PDF files are allowed.")
            return redirect('farmer_dashboard')

        try:
            # Fetch the farmer and financial institution
            farmer = Farmer.objects.get(farmer_id=farmer_id)
            print("Farmer fetched successfully.")

            financial_institution_obj = FinancialInstitution.objects.get(name=financial_institution)
            print("Financial Institution fetched successfully.")

            # Create loan application
            loan_application = LoanApplication.objects.create(
                farmer=farmer,
                financial_institution=financial_institution_obj,
                loan_pdf=loan_pdf,
                loan_status='Pending'
            )

            # Print the file path after saving
            print(f"File saved at: {loan_application.loan_pdf.path}")

            # Redirect with success message
            messages.success(request, "Loan application submitted successfully.")
            return HttpResponseRedirect(reverse('farmer_dashboard') + '?loan_submitted=true')


        except Farmer.DoesNotExist:
            print("Error: Farmer not found.")
            messages.error(request, "Farmer not found.")
            return redirect('farmer_dashboard')

        except FinancialInstitution.DoesNotExist:
            print("Error: Financial Institution not found.")
            messages.error(request, "Selected financial institution not found.")
            return redirect('farmer_dashboard')

        except Exception as e:
            print(f"Unexpected error: {e}")
            messages.error(request, "An unexpected error occurred.")
            return redirect('farmer_dashboard')

    print("Request method is not POST.")
    messages.error(request, "Invalid request method.")
    return redirect('farmer_dashboard')

# Loan application view for the cooperatives

def apply_for_loan_cooperative(request):
    if request.method == 'POST':
        print("POST data:", request.POST)
        print("Form submission started.")

        # Fetch form data
        coop_id = request.POST.get('coop_id')
        financial_institution_name = request.POST.get('financial_institution')
        loan_pdf = request.FILES.get('loan_pdf')

        # Print debug information
        print(f"Cooperative ID: {coop_id}")
        print(f"Financial Institution: {financial_institution_name}")
        print(f"Uploaded File: {loan_pdf}")

        # Validate form data
        if not coop_id:
            print("Cooperative ID is missing.")
            messages.error(request, "Cooperative ID is required.")
            return redirect('cooperative_dashboard')

        if not financial_institution_name:
            print("Financial Institution is missing.")
            messages.error(request, "Financial institution is required.")
            return redirect('cooperative_dashboard')

        if not loan_pdf:
            print("File upload failed: No file received.")
            messages.error(request, "Loan form (PDF) is required.")
            return redirect('cooperative_dashboard')

        if not loan_pdf.name.endswith('.pdf'):
            print("Invalid file type.")
            messages.error(request, "Only PDF files are allowed.")
            return redirect('cooperative_dashboard')

        try:
            # Fetch the cooperative and financial institution objects
            cooperative = Cooperative.objects.get(coop_id=coop_id)
            print("Cooperative fetched successfully.")

            financial_institution_obj = FinancialInstitution.objects.get(name=financial_institution_name)
            print("Financial Institution fetched successfully.")

            # Create loan application for cooperative
            loan_application = LoanApplicationCooperative.objects.create(
                cooperative=cooperative,
                financial_institution=financial_institution_obj,
                loan_pdf=loan_pdf,
                loan_status='Pending'
            )

            # Print the file path after saving
            print(f"File saved at: {loan_application.loan_pdf.path}")

            # Redirect with success message
            messages.success(request, "Loan application submitted successfully.")
            return HttpResponseRedirect(reverse('cooperative_dashboard') + '?loan_submitted=true')

        except Cooperative.DoesNotExist:
            print("Error: Cooperative not found.")
            messages.error(request, "Cooperative not found.")
            return redirect('cooperative_dashboard')

        except FinancialInstitution.DoesNotExist:
            print("Error: Financial Institution not found.")
            messages.error(request, "Selected financial institution not found.")
            return redirect('cooperative_dashboard')

        except Exception as e:
            print(f"Unexpected error: {e}")
            messages.error(request, f"An unexpected error occurred: {e}")
            return redirect('cooperative_dashboard')
        
    print("Request method is not POST.")
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
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json

def update_loan_status(request, loan_id):
    if request.method == 'POST':
        try:
            # Log the incoming request and data
            print(f"Received POST request for loan ID: {loan_id}")
            data = json.loads(request.body)
            print(f"Request data: {data}")

            # Extract and validate the new status
            new_status = data.get('status')
            print(f"New status received: {new_status}")

            valid_statuses = ['Received', 'Under Review', 'Approved', 'Denied']
            if new_status not in valid_statuses:
                print(f"Invalid status: {new_status}")
                return JsonResponse({'success': False, 'error': f'Invalid status: {new_status}'})

            # Fetch the loan application using the loan_id
            application = get_object_or_404(LoanApplication, loan_id=loan_id)
            print(f"Loan application found: {application}")

            # Update the status
            application.loan_status = new_status
            application.save()
            print(f"Loan status updated to: {new_status}")

            # Return a success response with a message
            return JsonResponse({'success': True, 'message': f'Status updated to "{new_status}" successfully!'})
        except LoanApplication.DoesNotExist:
            print(f"Loan application not found for ID: {loan_id}")
            return JsonResponse({'success': False, 'error': 'Loan application not found'})
        except json.JSONDecodeError:
            print("Error decoding JSON data")
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    elif request.method == 'GET':
        try:
            print(f"Received GET request for loan ID: {loan_id}")

            # Fetch the loan application using the loan_id
            application = get_object_or_404(LoanApplication, loan_id=loan_id)
            print(f"Loan application found: {application}")

            # Return the current status
            return JsonResponse({'success': True, 'status': application.loan_status})
        except LoanApplication.DoesNotExist:
            print(f"Loan application not found for ID: {loan_id}")
            return JsonResponse({'success': False, 'error': 'Loan application not found'})
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    else:
        print(f"Invalid request method: {request.method}")
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

# update loan status for the cooperative
def update_cooperative_loan_status(request, application_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_status = data.get('status')

            # Query the LoanApplicationCooperative model
            loan_application = LoanApplicationCooperative.objects.filter(loan_id=application_id).first()

            if not loan_application:
                return JsonResponse({'success': False, 'error': 'No LoanApplicationCooperative matches the given query'})

            # Update the loan status
            loan_application.loan_status = new_status
            loan_application.save()

            # Return success response
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

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

def update_farmer_profile(request):
    if request.method == 'POST':
        user = request.user
        farmer = Farmer.objects.get(user=user)

        # Update Farmer profile fields
        farmer.full_name = request.POST.get('full_name', farmer.full_name)
        farmer.phone_number = request.POST.get('phone_number', farmer.phone_number)
        farmer.farm_location = request.POST.get('farm_location', farmer.farm_location)
        farmer.crop_type = request.POST.get('crop_type', farmer.crop_type)
        farmer.farm_size = request.POST.get('farm_size', farmer.farm_size)

        # Update password if provided
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password and confirm_password:
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # Keeps the user logged in after password change
                messages.success(request, "Password updated successfully.")
            else:
                messages.error(request, "Passwords do not match.")
                return redirect('farmer_dashboard')

        # Save farmer profile updates
        farmer.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('farmer_dashboard')

    messages.error(request, "Invalid request method.")
    return redirect('farmer_dashboard')

def update_cooperative_profile(request):
    if request.method == 'POST':
        user = request.user
        cooperative = Cooperative.objects.get(user=user)

        # Update Cooperative profile fields
        cooperative.name = request.POST.get('name', cooperative.name)
        cooperative.phone_number = request.POST.get('phone_number', cooperative.phone_number)
        cooperative.location = request.POST.get('location', cooperative.location)
        cooperative.registration_number = request.POST.get('registration_number', cooperative.registration_number)
        cooperative.number_of_members = request.POST.get('number_of_members', cooperative.number_of_members)
        cooperative.performance_status = request.POST.get('performance_status', cooperative.performance_status)

        # Update password if provided
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password and confirm_password:
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # Keeps the user logged in after password change
                messages.success(request, "Password updated successfully.")
            else:
                messages.error(request, "Passwords do not match.")
                return redirect('cooperative_dashboard')

        # Save cooperative profile updates
        cooperative.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('cooperative_dashboard')

    messages.error(request, "Invalid request method.")
    return redirect('cooperative_dashboard')

def update_financial_institution_profile(request):
    if request.method == 'POST':
        user = request.user
        financial_institution = FinancialInstitution.objects.get(user=user)

        # Update Financial Institution profile fields
        financial_institution.name = request.POST.get('name', financial_institution.name)
        financial_institution.email = request.POST.get('email', financial_institution.email)
        financial_institution.institution_type = request.POST.get('institution_type', financial_institution.institution_type)
        financial_institution.phone_number = request.POST.get('phone_number', financial_institution.phone_number)
        financial_institution.license_number = request.POST.get('license_number', financial_institution.license_number)
        financial_institution.address = request.POST.get('address', financial_institution.address)
        financial_institution.interest_rate_range = request.POST.get('interest_rate_range', financial_institution.interest_rate_range)

        # Update password if provided
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password and confirm_password:
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # Keeps the user logged in after password change
                messages.success(request, "Password updated successfully.")
            else:
                messages.error(request, "Passwords do not match.")
                return redirect('financial_institution_dashboard')

        # Save financial institution profile updates
        financial_institution.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('financial_institution_dashboard')

    messages.error(request, "Invalid request method.")
    return redirect('financial_institution_dashboard')
