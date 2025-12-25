from django.contrib import admin
from .models import Project, Milestone, ProjectTemplate


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """后台管理：项目列表配置"""
    list_display = ("name", "owner", "status", "priority", "created_at", "is_active")
    list_filter = ("status", "priority", "is_active")
    search_fields = ("name", "owner__username")


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    """后台管理：里程碑列表配置"""
    list_display = ("project", "name", "due_date", "completed")
    list_filter = ("completed", "due_date")
    search_fields = ("project__name", "name")


@admin.register(ProjectTemplate)
class ProjectTemplateAdmin(admin.ModelAdmin):
    """后台管理：项目模板配置"""
    list_display = ("name", "category", "is_public", "created_by", "created_at")
    list_filter = ("category", "is_public")
    search_fields = ("name", "created_by__username")
