from django.urls import path
from electionhistory import views


urlpatterns = [
    path('', views.ElectionHistoryList.as_view()),
    path('vote', views.vote),
]