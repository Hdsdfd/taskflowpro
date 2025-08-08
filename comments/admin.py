from django.contrib import admin
from .models import Comment, CommentLike

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'task', 'short_content', 'created_at', 'parent', 'like_count']
    list_filter = ['created_at', 'author']
    search_fields = ['content', 'author__username', 'task__title']
    readonly_fields = ['created_at', 'updated_at']
    
    def short_content(self, obj):
        return obj.short_content
    short_content.short_description = '评论内容'

@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'comment', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username', 'comment__content']
