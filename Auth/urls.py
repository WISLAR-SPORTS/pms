from django.apps import AppConfig
from django.urls import path
from .views import student_register, load_departments,log, login, student_dashboard, profile, edit_profile
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView



app_name = "auth" 

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', student_register, name='student_register'),
    #path('ajax/load-branches/', load_branches, name='ajax_load_branches'),
    
    path('load-departments/', load_departments, name='load_departments'),
    path('login/', login, name='login'),
    path('dashboard/', student_dashboard, name='dashboard'),
    #path('change-password/', change_password, name='change_password'),
    path('logout/', log, name='logout'),
    path('profile/', profile, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
]