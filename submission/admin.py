from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Submission

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'project',  'student', 'submitted_at', 'approved')
    list_filter = ('approved', 'project')
    search_fields = ('title', 'student__username', 'project__title')