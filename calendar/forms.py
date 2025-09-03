from django import forms
from .models import CalendarEvent

class CalendarEventForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = ['title', 'description', 'event_type', 'priority', 'start_time', 'end_time', 'all_day', 'is_recurring', 'recurrence_rule', 'recurrence_end', 'project', 'task', 'attendees', 'location', 'reminder_minutes']
