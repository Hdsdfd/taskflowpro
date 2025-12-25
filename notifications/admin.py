from django.contrib import admin
from .models import Notification, NotificationTemplate, UserNotificationSettings

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'priority', 'is_read', 'created_at']
    list_filter = ['notification_type', 'priority', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'title', 'message']
    readonly_fields = ['created_at', 'read_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('recipient', 'notification_type', 'title', 'message', 'priority')
        }),
        ('关联对象', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('状态信息', {
            'fields': ('is_read', 'is_sent', 'channels', 'created_at', 'read_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} 个通知已标记为已读')
    mark_as_read.short_description = '标记为已读'
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} 个通知已标记为未读')
    mark_as_unread.short_description = '标记为未读'

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'notification_type', 'is_active', 'created_at']
    list_filter = ['notification_type', 'is_active', 'created_at']
    search_fields = ['name', 'title_template', 'message_template']
    ordering = ['name']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'notification_type', 'is_active')
        }),
        ('模板内容', {
            'fields': ('title_template', 'message_template')
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

@admin.register(UserNotificationSettings)
class UserNotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_notifications', 'site_notifications', 'browser_notifications', 'created_at']
    list_filter = ['email_notifications', 'site_notifications', 'browser_notifications', 'created_at']
    search_fields = ['user__username', 'user__email']
    ordering = ['user__username']
    
    fieldsets = (
        ('用户信息', {
            'fields': ('user',)
        }),
        ('邮件通知', {
            'fields': ('email_notifications', 'email_frequency')
        }),
        ('站内通知', {
            'fields': ('site_notifications', 'browser_notifications')
        }),
        ('特定类型通知', {
            'fields': ('task_notifications', 'project_notifications', 'comment_notifications', 'file_notifications'),
            'classes': ('collapse',)
        }),
        ('免打扰时间', {
            'fields': ('quiet_hours_start', 'quiet_hours_end'),
            'classes': ('collapse',)
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
