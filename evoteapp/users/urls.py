from django.urls import path
from users import views

urlpatterns = [
    path('user-list/', views.UserList.as_view()),
]