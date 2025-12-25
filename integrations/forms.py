from django import forms
from .models import ThirdPartyService

class ThirdPartyServiceForm(forms.ModelForm):
    class Meta:
        model = ThirdPartyService
        fields = ['name', 'service_type', 'description', 'base_url', 'api_version', 'documentation_url', 'auth_type', 'is_active', 'is_public']
