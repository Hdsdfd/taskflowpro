from django.contrib import admin
from .models import FileCategory, ProjectFile, FileVersion, FileComment

@admin.register(FileCategory)
class FileCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'color', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    ordering = ['name']

@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'file_type', 'file_size_mb', 'uploaded_by', 'uploaded_at', 'download_count']
    list_filter = ['file_type', 'uploaded_at', 'is_public']
    search_fields = ['name', 'description', 'project__name', 'uploaded_by__username']
    readonly_fields = ['file_size', 'mime_type', 'download_count']
    ordering = ['-uploaded_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'original_name', 'file', 'file_type', 'description')
        }),
        ('关联信息', {
            'fields': ('project', 'task', 'category', 'tags')
        }),
        ('权限设置', {
            'fields': ('is_public', 'uploaded_by')
        }),
        ('系统信息', {
            'fields': ('file_size', 'mime_type', 'download_count', 'uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(FileVersion)
class FileVersionAdmin(admin.ModelAdmin):
    list_display = ['file', 'version_number', 'file_size', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['file__name', 'version_number', 'uploaded_by__username']
    ordering = ['-uploaded_at']

@admin.register(FileComment)
class FileCommentAdmin(admin.ModelAdmin):
    list_display = ['file', 'author', 'content_preview', 'parent', 'created_at']
    list_filter = ['created_at']
    search_fields = ['file__name', 'author__username', 'content']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        """内容预览"""
        if len(obj.content) > 50:
            return obj.content[:50] + '...'
        return obj.content
    content_preview.short_description = '内容预览'
