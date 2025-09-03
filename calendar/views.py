from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from .models import CalendarEvent
from .forms import CalendarEventForm

class CalendarEventListView(LoginRequiredMixin, ListView):
    model = CalendarEvent
    template_name = 'calendar/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        user = self.request.user
        return CalendarEvent.objects.filter(attendees=user) | CalendarEvent.objects.filter(creator=user)

class CalendarEventDetailView(LoginRequiredMixin, DetailView):
    model = CalendarEvent
    template_name = 'calendar/event_detail.html'
    context_object_name = 'event'

class CalendarEventCreateView(LoginRequiredMixin, CreateView):
    model = CalendarEvent
    form_class = CalendarEventForm
    template_name = 'calendar/event_form.html'
    success_url = reverse_lazy('calendar:event_list')

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)
