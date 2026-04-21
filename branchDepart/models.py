from django.db import models

# Create your models here
# from django.db import models



class Branch(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    
    
    def __str__(self):
        return self.name 

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="departments")
    
    def __str__(self):
        return f"{self.branch.name} ({self.name})" 


class Program(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="programs")
    duration_years = models.PositiveSmallIntegerField(default=4)  # optional

    def __str__(self):
        return f"{self.department.code}-{self.code}"