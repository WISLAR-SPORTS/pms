from django.db import models

# Create your models here.
from django.db import models
from project.models import Project
from Auth.models import CustomUser



class Submission(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="submissions")
   
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    is_seen = models.BooleanField(default=False)
    
    
    def __str__(self):
        return f"{self.project.title} - {self.title}"