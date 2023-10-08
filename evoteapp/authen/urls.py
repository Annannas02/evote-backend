from django.urls import path
from authen import views


"""
POST auth/register
POST 2fa/generate
POST 2fa/authenticate
POST auth/generate-token
POST auth/verify-token
"""

urlpatterns = [
    path('auth/register', views.RegisterUserView.as_view()),
    path('2fa/generate', views.generate_totp),
    path('2fa/authenticate', views.authenticate_2fa)
]