from drf_yasg import openapi

# Farmer Registration Schema
farmer_register_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['full_name', 'email', 'password', 'phone_number', 'farm_location', 'crop_types'],
    properties={
        'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='Full name of the farmer'),
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the farmer'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password for the farmer\'s account'),
        'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number of the farmer'),
        'farm_location': openapi.Schema(type=openapi.TYPE_STRING, description='Location of the farm'),
        'crop_types': openapi.Schema(type=openapi.TYPE_STRING, description='Types of crops grown (e.g., "Maize, Wheat")'),
        'farm_size': openapi.Schema(type=openapi.TYPE_NUMBER, description='Farm size in hectares (optional)'),
        'cooperative_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid', description='UUID of the Cooperative (optional)'),
    }
)

# Cooperative Registration Schema
cooperative_register_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['name', 'location', 'registration_number'],
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the cooperative'),
        'location': openapi.Schema(type=openapi.TYPE_STRING, description='Location of the cooperative'),
        'registration_number': openapi.Schema(type=openapi.TYPE_STRING, description='Unique registration number of the cooperative'),
        'number_of_farmers': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of farmers in the cooperative'),
        'performance_status': openapi.Schema(type=openapi.TYPE_STRING, description='Performance status (e.g., "High", "Moderate")'),
    }
)

# Cooperative Manager Registration Schema
cooperative_manager_register_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['full_name', 'email', 'password', 'phone_number', 'cooperative_id'],
    properties={
        'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='Full name of the cooperative manager'),
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the cooperative manager'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password for the cooperative manager\'s account'),
        'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number of the cooperative manager'),
        'cooperative_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid', description='UUID of the cooperative associated with the manager'),
    }
)

# Financial Institution Registration Schema
financial_institution_register_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['name', 'institution_type', 'email', 'password', 'phone_number', 'license_number', 'address'],
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the financial institution'),
        'institution_type': openapi.Schema(type=openapi.TYPE_STRING, description='Type of institution (e.g., "Bank", "Microfinance")'),
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the institution'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password for the financial institution\'s account'),
        'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number of the institution'),
        'license_number': openapi.Schema(type=openapi.TYPE_STRING, description='Unique license number of the institution'),
        'address': openapi.Schema(type=openapi.TYPE_STRING, description='Address of the institution'),
        'interest_rate_range': openapi.Schema(type=openapi.TYPE_STRING, description='Interest rate range offered (e.g., "3%-8%")'),
    }
)

# Loan Application Schema
loan_application_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['farmer_id', 'financial_institution_id', 'loan_amount'],
    properties={
        'farmer_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid', description='UUID of the farmer applying for the loan'),
        'cooperative_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid', description='UUID of the cooperative (optional)'),
        'financial_institution_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid', description='UUID of the financial institution offering the loan'),
        'loan_amount': openapi.Schema(type=openapi.TYPE_NUMBER, format='decimal', description='Requested loan amount'),
        'loan_status': openapi.Schema(type=openapi.TYPE_STRING, description='Status of the loan application (e.g., "Pending", "Approved")'),
        'submission_date': openapi.Schema(type=openapi.FORMAT_DATETIME, description='Date and time the loan was submitted'),
    }
)

# OTP Request Schema
otp_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email'],
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address to send the OTP to')
    }
)

# OTP Verification Schema
otp_verification_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'otp'],
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address used to request the OTP'),
        'otp': openapi.Schema(type=openapi.TYPE_STRING, description='OTP code sent to the email'),
    }
)

# Signin Schema
signin_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'password'],
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address of the user'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password of the user'),
    },
    example={
        'email': 'john@example.com',
        'password': 'password123',
    }
)

# Signin Response Schema
signin_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='JWT Refresh Token'),
        'access': openapi.Schema(type=openapi.TYPE_STRING, description='JWT Access Token'),
        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
    },
    example={
        'refresh': 'some-refresh-token',
        'access': 'some-access-token',
        'message': 'Login successful',
    }
)
