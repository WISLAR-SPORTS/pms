from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import AnalyticsMetric

@admin.register(AnalyticsMetric)
class AnalyticsMetricAdmin(admin.ModelAdmin):
    list_display = ('project', 'metric_name', 'value', 'recorded_at')
    list_filter = ('metric_name', 'project')
    search_fields = ('metric_name', 'project__title')