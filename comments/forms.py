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