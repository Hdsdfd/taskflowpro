from django.contrib import admin
from .models import UserProfile, PasswordResetCode


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """后台管理：用户档案列表配置"""
    list_display = ("user", "role", "created_at", "updated_at")
    list_filter = ("role", "created_at")
    search_fields = ("user__username", "user__email")


@admin.register(PasswordResetCode)
class PasswordResetCodeAdmin(admin.ModelAdmin):
    """后台管理：找回密码验证码记录"""
    list_display = ("user", "code", "is_used", "created_at", "expires_at")
    list_filter = ("is_used", "created_at")
    search_fields = ("user__username", "code")
