from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Feedback, TestFeedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('submission', 'supervisor', 'created_at')
    list_filter = ('supervisor',)
    search_fields = ('submission__title', 'supervisor__user__username')


@admin.register(TestFeedback)
class TestFeedbackAdmin(admin.ModelAdmin):
    list_display = ('email', 'message','screenshot','created_at')
    search_fields = ('email', 'message')