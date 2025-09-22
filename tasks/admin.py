from django.contrib import admin
from .models import Task, TaskTag, TaskDependency, TimeEntry


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """后台管理：任务列表配置"""
    list_display = ("title", "project", "assignee", "priority", "status", "due_date", "order")
    list_filter = ("priority", "status", "project")
    search_fields = ("title", "project__name", "assignee__username")


@admin.register(TaskTag)
class TaskTagAdmin(admin.ModelAdmin):
    """后台管理：任务标签配置"""
    list_display = ("name", "color", "created_at")
    search_fields = ("name",)


@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    """后台管理：任务依赖配置"""
    list_display = ("prerequisite_task", "dependent_task", "dependency_type", "lag_days")
    list_filter = ("dependency_type",)
    search_fields = ("prerequisite_task__title", "dependent_task__title")


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    """后台管理：工时记录配置"""
    list_display = ("task", "user", "start_time", "end_time", "duration_hours")
    list_filter = ("start_time",)
    search_fields = ("task__title", "user__username")
