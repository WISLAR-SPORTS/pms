from django.db import models

# Create your models here.
# Analytics can be computed dynamically, so you might not need DB models
# But for stored metrics:
from django.db import models
from project.models import Project

class AnalyticsMetric(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    metric_name = models.CharField(max_length=50)
    value = models.FloatField()
    recorded_at = models.DateTimeField(auto_now_add=True)