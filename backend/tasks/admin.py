from django.contrib import admin
from .models import Task, TaskStep, TaskMessage, StatusHistory


class TaskStepInline(admin.TabularInline):
    model = TaskStep
    extra = 0


class TaskMessageInline(admin.TabularInline):
    model = TaskMessage
    extra = 0
    readonly_fields = ['created_at']


class StatusHistoryInline(admin.TabularInline):
    model = StatusHistory
    extra = 0
    readonly_fields = ['changed_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['task_code', 'intent', 'status', 'risk_level', 'risk_score', 'assigned_team', 'created_at']
    list_filter = ['intent', 'status', 'risk_level', 'assigned_team']
    search_fields = ['task_code', 'original_request']
    readonly_fields = ['id', 'task_code', 'created_at', 'updated_at']
    inlines = [TaskStepInline, TaskMessageInline, StatusHistoryInline]


@admin.register(TaskStep)
class TaskStepAdmin(admin.ModelAdmin):
    list_display = ['task', 'step_number', 'title', 'is_complete']


@admin.register(TaskMessage)
class TaskMessageAdmin(admin.ModelAdmin):
    list_display = ['task', 'channel', 'created_at']


@admin.register(StatusHistory)
class StatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['task', 'old_status', 'new_status', 'changed_at']
