from django.urls import path
from electionhistory import views


urlpatterns = [
    path('', views.ElectionHistoryList.as_view()),
    path('vote', views.vote),
    path('vote/status', views.delete_user_vote),
]