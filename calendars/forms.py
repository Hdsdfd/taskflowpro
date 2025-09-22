from django import forms
from .models import calendarsEvent

class calendarsEventForm(forms.ModelForm):
    """日历事件表单：用于创建/编辑事件"""
    class Meta:
        model = calendarsEvent
        fields = ['title', 'description', 'event_type', 'priority', 'start_time', 'end_time', 'all_day', 'is_recurring', 'recurrence_rule', 'recurrence_end', 'project', 'task', 'attendees', 'location', 'reminder_minutes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入事件标题'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '事件描述'}),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'all_day': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'recurrence_rule': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RRULE 如 FREQ=WEEKLY;INTERVAL=1'}),
            'recurrence_end': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'task': forms.Select(attrs={'class': 'form-control'}),
            'attendees': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '会议地点或地址'}),
            'reminder_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
