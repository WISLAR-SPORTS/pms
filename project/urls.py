from django.urls import path
from project import views

app_name = "project" 

urlpatterns = [
    path('submit/', views.submit_project, name='submit_project'),
    path('ajax/load-departments/', views.load_departments, name='ajax_load_departments'),
    path('ajax/load-programs/', views.load_programs, name='ajax_load_programs'),
    path("projects/", views.supervisor_projects, name="sprojects"),
    path("projects/approve/<int:project_id>/", views.approve_project, name="approve_project"),
    path("projects/decline/<int:project_id>/", views.decline_project, name="decline_project"),
    path("feedback/project/<int:project_id>/", views.give_feedback, name="give_feedback"),
     path("feedback/chat/<int:project_id>/", views.project_feedback_chat, name="feedback_chat"),

]