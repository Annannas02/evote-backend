from django.urls import path
from users import views

urlpatterns = [
    path('user-list/', views.UserList.as_view()),
    path('authenticated-user/', views.get_authenticated_user),
    path('<int:user_id>/', views.get_user_by_id)
]