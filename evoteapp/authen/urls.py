from django.urls import path
from authen import views


"""
POST auth/register
POST 2fa/generateOtp
POST 2fa/authenticate - generate JWT token, set it in the header
POST auth/generate-token
POST auth/verify-token
"""

urlpatterns = [
    path('auth/register', views.RegisterUserView.as_view()),
    path('2fa/generateOtp', views.generate_totp),
    path('2fa/authenticate', views.authenticate_2fa)
]