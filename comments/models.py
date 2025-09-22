from django.db import models
from django.contrib.auth.models import User
from tasks.models import Task

class Comment(models.Model):
    """
    评论模型 - 允许用户对任务进行评论，支持多级回复
    """
    # 关联被评论的任务与评论作者
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments', verbose_name='任务')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='评论者')
    content = models.TextField(verbose_name='评论内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    # 自引用外键：父评论，为空表示顶级评论
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE, verbose_name='父评论')
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.author.username} 对 {self.task.title} 的评论"
    
    @property
    def short_content(self):
        # 预览内容：超过100字符则截断显示
        if len(self.content) > 100:
            return self.content[:100] + '...'
        return self.content
    
    @property
    def like_count(self):
        # 点赞数量
        return self.likes.count()
    
    @property
    def has_replies(self):
        # 是否存在子回复
        return self.replies.exists()

class CommentLike(models.Model):
    # 评论点赞表：一条评论可被多用户点赞，同一用户对同一评论仅允许一次
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes', verbose_name='评论')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes', verbose_name='用户')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')
    
    class Meta:
        unique_together = ('comment', 'user')
        verbose_name = '评论点赞'
        verbose_name_plural = '评论点赞'
    
    def __str__(self):
        return f"{self.user.username} 点赞了 {self.comment.id}"
