from django.db import models

# Create your models here.
from django.db import models
from submission.models import Submission
from Supervisor.models import SupervisorProfile
from project.models import Project

class Feedback(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, null=True, blank=True, related_name="feedbacks")
    project = models.ForeignKey(Project, on_delete=models.CASCADE,null=True,
    blank=True, related_name="feedbacks")
    supervisor = models.ForeignKey(SupervisorProfile, on_delete=models.SET_NULL, null=True)
    comment = models.TextField()
    is_read = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
     return f"Feedback for {self.submission or self.project or 'unknown target'}"
    

from django.db import models

class TestFeedback(models.Model):
    email = models.EmailField()
    message = models.TextField()
    screenshot = models.ImageField(upload_to='feedback_screenshots/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.created_at.strftime('%Y-%m-%d')}"