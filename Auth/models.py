from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('supervisor', 'Supervisor'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES,  blank=True,
    null=True)
    
    # Fixed department reference to your model
    department = models.ForeignKey(
        'branchDepart.Department',  # app_label.model_name
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    enrollment_number = models.CharField(max_length=20, unique=True, null=True, blank=True)


    # Avoid clashes with built-in User model
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.'
    )
    def save(self, *args, **kwargs):
        # Auto-generate enrollment number for students
        if self.role == 'student' and not self.enrollment_number:
            # Example: ENR-YYYYMMDD-<random 4 digits>
            import datetime, random
            today = datetime.date.today().strftime("%Y%m%d")
            random_digits = str(random.randint(1000, 9999))
            self.enrollment_number = f"ENR-{today}-{random_digits}"
        super().save(*args, **kwargs)