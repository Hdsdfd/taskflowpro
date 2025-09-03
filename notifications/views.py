from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from .models import Notification
from .forms import NotificationForm

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

class NotificationDetailView(LoginRequiredMixin, DetailView):
    model = Notification
    template_name = 'notifications/notification_detail.html'
    context_object_name = 'notification'

class NotificationCreateView(LoginRequiredMixin, CreateView):
    model = Notification
    form_class = NotificationForm
    template_name = 'notifications/notification_form.html'
    success_url = reverse_lazy('notifications:notification_list')
