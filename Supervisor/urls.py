from django.urls import path
from .views import supervisor_dashboard, profile, edit_profile, download_submission


app_name = 'supervisor'

urlpatterns = [
    path('sdashboard/', supervisor_dashboard, name='sdashboard'),
    path('sprofile/', profile, name='sprofile'),
    path('profile/sedit/', edit_profile, name='sedit_profile'),
     path('submission/download/<int:submission_id>/', download_submission, name='download_submission'),

   

]