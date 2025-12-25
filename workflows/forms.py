from django import forms
from .models import ApprovalRequest

class ApprovalRequestForm(forms.ModelForm):
    class Meta:
        model = ApprovalRequest
        fields = ['title', 'description', 'request_type', 'priority', 'project', 'task', 'deadline', 'attachments', 'notes']
