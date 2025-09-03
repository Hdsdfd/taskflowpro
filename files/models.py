from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from projects.models import Project
from tasks.models import Task
import os

class FileCategory(models.Model):
    """
    文件分类模型
    """
    name = models.CharField(max_length=100, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')
    color = models.CharField(max_length=7, default='#6c757d', verbose_name='分类颜色')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '文件分类'
        verbose_name_plural = '文件分类'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class ProjectFile(models.Model):
    """
    项目文件模型
    """
    FILE_TYPES = (
        ('document', '文档'),
        ('image', '图片'),
        ('video', '视频'),
        ('audio', '音频'),
        ('archive', '压缩包'),
        ('code', '代码'),
        ('other', '其他'),
    )
    
    name = models.CharField(max_length=255, verbose_name='文件名')
    original_name = models.CharField(max_length=255, verbose_name='原始文件名')
    file = models.FileField(upload_to='project_files/%Y/%m/%d/', verbose_name='文件')
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, verbose_name='文件类型')
    file_size = models.BigIntegerField(verbose_name='文件大小(字节)')
    mime_type = models.CharField(max_length=100, verbose_name='MIME类型')
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files', verbose_name='所属项目')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='files', null=True, blank=True, verbose_name='关联任务')
    category = models.ForeignKey(FileCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='文件分类')
    
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='上传者')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    description = models.TextField(blank=True, verbose_name='文件描述')
    tags = models.CharField(max_length=500, blank=True, verbose_name='标签')
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    download_count = models.IntegerField(default=0, verbose_name='下载次数')
    
    class Meta:
        verbose_name = '项目文件'
        verbose_name_plural = '项目文件'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.file_size and self.file:
            self.file_size = self.file.size
        if not self.mime_type and self.file:
            import mimetypes
            self.mime_type = mimetypes.guess_type(self.file.name)[0] or 'application/octet-stream'
        super().save(*args, **kwargs)
    
    @property
    def file_size_mb(self):
        """文件大小(MB)"""
        return round(self.file_size / (1024 * 1024), 2)
    
    @property
    def file_extension(self):
        """文件扩展名"""
        return os.path.splitext(self.original_name)[1].lower()
    
    def increment_download_count(self):
        """增加下载次数"""
        self.download_count += 1
        self.save(update_fields=['download_count'])

class FileVersion(models.Model):
    """
    文件版本模型
    """
    file = models.ForeignKey(ProjectFile, on_delete=models.CASCADE, related_name='versions', verbose_name='文件')
    version_number = models.CharField(max_length=20, verbose_name='版本号')
    file = models.FileField(upload_to='file_versions/%Y/%m/%d/', verbose_name='版本文件')
    file_size = models.BigIntegerField(verbose_name='文件大小(字节)')
    
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='上传者')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    change_log = models.TextField(blank=True, verbose_name='变更说明')
    
    class Meta:
        verbose_name = '文件版本'
        verbose_name_plural = '文件版本'
        ordering = ['-uploaded_at']
        unique_together = ('file', 'version_number')
    
    def __str__(self):
        return f"{self.file.name} v{self.version_number}"

class FileComment(models.Model):
    """
    文件评论模型
    """
    file = models.ForeignKey(ProjectFile, on_delete=models.CASCADE, related_name='comments', verbose_name='文件')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='评论者')
    content = models.TextField(verbose_name='评论内容')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies', verbose_name='父评论')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '文件评论'
        verbose_name_plural = '文件评论'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.author.username} 对 {self.file.name} 的评论"
