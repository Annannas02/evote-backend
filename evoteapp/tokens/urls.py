from django.urls import path
from tokens import views


urlpatterns = [
    path('', views.TokenList.as_view())
]