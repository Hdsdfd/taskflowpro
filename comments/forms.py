from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    """
    评论表单
    """
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入您的评论...'
            })
        }
        labels = {
            'content': '评论内容'
        }

class ReplyCommentForm(forms.ModelForm):
    """回复评论表单：与 CommentForm 一致但可配置不同的 UI 行数"""
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': '回复内容...'
            })
        }
        labels = {
            'content': '回复内容'
        } 