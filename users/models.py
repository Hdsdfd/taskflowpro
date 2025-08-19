from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserProfile(models.Model):
    """
    用户扩展信息模型
    """

    USER_ROLES = (
        ('admin', '管理员'),
        ('member', '普通成员'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=USER_ROLES, default='member', verbose_name='用户角色')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='头像')
    bio = models.TextField(max_length=500, blank=True, verbose_name='个人简介')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户档案'
        verbose_name_plural = '用户档案'
    
    def __str__(self):
        
        return f"{self.user.username} - {self.get_role_display()}"
    
    @property
    def is_admin(self):
        return self.role == 'admin'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """创建用户时自动创建用户档案"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """保存用户时自动保存用户档案"""
    instance.profile.save()


class PasswordResetCode(models.Model):
    """
    找回密码邮箱验证码
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_codes', verbose_name='用户')
    code = models.CharField(max_length=6, verbose_name='验证码')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    is_used = models.BooleanField(default=False, verbose_name='是否已使用')

    class Meta:
        verbose_name = '找回密码验证码'
        verbose_name_plural = '找回密码验证码'
        indexes = [
            models.Index(fields=['user', 'code', 'is_used']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}-{self.code}"

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at