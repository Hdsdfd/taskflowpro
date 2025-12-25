from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from .models import ProjectReport
from .forms import ProjectReportForm

class ProjectReportListView(LoginRequiredMixin, ListView):
    model = ProjectReport
    template_name = 'analytics/report_list.html'
    context_object_name = 'reports'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ProjectReport.objects.all().order_by('-generated_at')
        return ProjectReport.objects.filter(project__members=user).order_by('-generated_at')

class ProjectReportDetailView(LoginRequiredMixin, DetailView):
    model = ProjectReport
    template_name = 'analytics/report_detail.html'
    context_object_name = 'report'

class ProjectReportCreateView(LoginRequiredMixin, CreateView):
    model = ProjectReport
    form_class = ProjectReportForm
    template_name = 'analytics/report_form.html'
    success_url = reverse_lazy('analytics:report_list')

    def form_valid(self, form):
        form.instance.generated_by = self.request.user
        return super().form_valid(form)
