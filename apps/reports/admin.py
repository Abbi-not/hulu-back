from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'reason', 'target_type', 'target_id', 'reporter', 'status', 'created_at']
    list_filter = ['status', 'reason', 'target_type']
    search_fields = ['reporter__email', 'reporter__username', 'target_id', 'description']
    readonly_fields = ['id', 'reporter', 'target_type', 'target_id', 'target_preview', 'reason', 'description', 'created_at', 'updated_at']
    ordering = ['-created_at']