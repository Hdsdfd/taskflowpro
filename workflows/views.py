from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from .models import ApprovalRequest
from .forms import ApprovalRequestForm

class ApprovalRequestListView(LoginRequiredMixin, ListView):
    model = ApprovalRequest
    template_name = 'workflows/approval_list.html'
    context_object_name = 'requests'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ApprovalRequest.objects.all().order_by('-created_at')
        return ApprovalRequest.objects.filter(requester=user).order_by('-created_at')

class ApprovalRequestDetailView(LoginRequiredMixin, DetailView):
    model = ApprovalRequest
    template_name = 'workflows/approval_detail.html'
    context_object_name = 'request_obj'

class ApprovalRequestCreateView(LoginRequiredMixin, CreateView):
    model = ApprovalRequest
    form_class = ApprovalRequestForm
    template_name = 'workflows/approval_form.html'
    success_url = reverse_lazy('workflows:approval_list')

    def form_valid(self, form):
        form.instance.requester = self.request.user
        return super().form_valid(form)
