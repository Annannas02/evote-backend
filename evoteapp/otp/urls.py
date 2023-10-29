from django.urls import path
from otp import views


urlpatterns = [
    path('', views.OtpList.as_view())
]