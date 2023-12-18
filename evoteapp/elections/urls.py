from django.urls import path
from elections import views


urlpatterns = [
    path('', views.ElectionsList.as_view()),
    path('extended-elections/', views.get_elections),
    path('extended-elections/<int:election_id>', views.get_election_by_id)
]