from django import forms
from .models import ProjectReport

class ProjectReportForm(forms.ModelForm):
    class Meta:
        model = ProjectReport
        fields = ['project', 'report_type', 'title', 'content', 'period_start', 'period_end']
