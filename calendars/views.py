from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from .models import calendarsEvent
from .forms import calendarsEventForm

class calendarsEventListView(LoginRequiredMixin, ListView):
    model = calendarsEvent
    template_name = 'calendars/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        user = self.request.user
        return calendarsEvent.objects.filter(attendees=user) | calendarsEvent.objects.filter(creator=user)

class calendarsEventDetailView(LoginRequiredMixin, DetailView):
    model = calendarsEvent
    template_name = 'calendars/event_detail.html'
    context_object_name = 'event'

class calendarsEventCreateView(LoginRequiredMixin, CreateView):
    model = calendarsEvent
    form_class = calendarsEventForm
    template_name = 'calendars/event_form.html'
    success_url = reverse_lazy('calendars:event_list')

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)
