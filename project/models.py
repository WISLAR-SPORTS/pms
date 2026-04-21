

from smart_selects.db_fields import ChainedForeignKey
from django.db import models
from Auth.models import CustomUser
from Supervisor.models import SupervisorProfile
from branchDepart.models import Branch, Department, Program
from django.core.exceptions import ValidationError

class Project(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="projects")

    

    supervisors = models.ManyToManyField(SupervisorProfile, related_name="projects")
    students = models.ManyToManyField(CustomUser, related_name="projects", limit_choices_to={'role': 'student'})
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    def clean(self):   # 👈 HERE
        if self.department and self.branch:
            if self.department.branch != self.branch:
                raise ValidationError("Department must belong to selected branch")
    
    def __str__(self):
        return self.title