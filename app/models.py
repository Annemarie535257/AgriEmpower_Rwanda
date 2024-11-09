from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

def get_expiry_time():
    return timezone.now() + timezone.timedelta(minutes=15)

class Cooperative(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    coop_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed passwords, usually using Django's authentication system
    phone_number = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True)
    number_of_members = models.PositiveIntegerField()
    performance_status = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

class Farmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    farmer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Passwords should be hashed in production
    phone_number = models.CharField(max_length=20)
    farm_location = models.CharField(max_length=255)
    crop_types = models.CharField(max_length=255)  # A single field for simplicity; can be changed to a ManyToMany if needed
    farm_size = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Farm size in hectares, optional

    def __str__(self):
        return self.full_name

class FinancialInstitution(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    fin_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    institution_type = models.CharField(max_length=100)  # e.g., Bank, Microfinance
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Passwords should be hashed in production
    phone_number = models.CharField(max_length=20)
    license_number = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=255)
    interest_rate_range = models.CharField(max_length=50, blank=True, null=True)  # Optional field for interest rate range

    def __str__(self):
        return self.name

class LoanApplication(models.Model):
    loan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    financial_institution = models.ForeignKey(FinancialInstitution, on_delete=models.CASCADE)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    loan_status = models.CharField(max_length=20, default='Pending')
    submission_date = models.DateTimeField(auto_now_add=True)

class OTP(models.Model):
    email = models.CharField(max_length=255)  # Increased max_length to allow more characters
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField(default=get_expiry_time)

    # Explicitly set objects manager
    objects = models.Manager()

    def __str__(self):
        return f'OTP for {self.email}'
