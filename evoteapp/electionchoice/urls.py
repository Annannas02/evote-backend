from django.urls import path
from electionchoice import views


urlpatterns = [
    path('', views.ElectionChoiceList.as_view())
]