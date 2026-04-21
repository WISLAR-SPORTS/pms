# submissions/urls.py
from django.urls import path
from .views import submit_progress, submission_detail

app_name = "submission"

urlpatterns = [
    path('submit/', submit_progress, name='submit'),
    path('submission/<int:pk>/',submission_detail, name='submission_detail'),
]