"""
URL configuration for authentication project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.shortcuts import render
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path, include
from django.contrib import admin
from app import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
   openapi.Info(
      title="Agriempower Rwanda API",
      default_version='v1',
      description="API documentation for Agriempower Rwanda",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="your-email@example.com"),
      license=openapi.License(name="BSD License"),
   ),
#    public=True,
#    permission_classes=(permissions.AllowAny,),
)

def homepage(request):
    # print("Home view called")
    return render(request, 'index.html')


urlpatterns = [

    # Swagger URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('admin/', admin.site.urls),

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
