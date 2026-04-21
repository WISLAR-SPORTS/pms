from django.db import models

# Create your models here.
from django.db import models
from Auth.models import CustomUser
from branchDepart.models import Department

class SupervisorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    office = models.CharField(max_length=50, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return self.user.username
