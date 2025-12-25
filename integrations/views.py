from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from .models import ThirdPartyService
from .forms import ThirdPartyServiceForm

class ThirdPartyServiceListView(LoginRequiredMixin, ListView):
    model = ThirdPartyService
    template_name = 'integrations/service_list.html'
    context_object_name = 'services'

    def get_queryset(self):
        return ThirdPartyService.objects.filter(is_active=True).order_by('name')

class ThirdPartyServiceDetailView(LoginRequiredMixin, DetailView):
    model = ThirdPartyService
    template_name = 'integrations/service_detail.html'
    context_object_name = 'service'

class ThirdPartyServiceCreateView(LoginRequiredMixin, CreateView):
    model = ThirdPartyService
    form_class = ThirdPartyServiceForm
    template_name = 'integrations/service_form.html'
    success_url = reverse_lazy('integrations:service_list')
