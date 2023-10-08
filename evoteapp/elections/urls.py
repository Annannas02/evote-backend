from django.urls import path
from elections import views


urlpatterns = [
    path('', views.ElectionsList.as_view())
]