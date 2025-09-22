from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from .models import calendarsEvent
from .forms import calendarsEventForm
from django.db.models import Q

class calendarsEventListView(LoginRequiredMixin, ListView):
    """事件列表：展示与当前用户相关的事件"""
    model = calendarsEvent
    template_name = 'calendars/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        # 逻辑解释：
        # - 基于 Q 条件过滤：当前用户为创建者或参与者；
        # - 使用 distinct 去重，避免重复记录（同一用户既是创建者又是参与者的情况）。
        user = self.request.user
        return calendarsEvent.objects.filter(Q(attendees=user) | Q(creator=user)).distinct().order_by('-start_time')

class calendarsEventDetailView(LoginRequiredMixin, DetailView):
    """事件详情"""
    model = calendarsEvent
    template_name = 'calendars/event_detail.html'
    context_object_name = 'event'

class calendarsEventCreateView(LoginRequiredMixin, CreateView):
    """创建事件：保存时补充创建者"""
    model = calendarsEvent
    form_class = calendarsEventForm
    template_name = 'calendars/event_form.html'
    success_url = reverse_lazy('calendars:event_list')

    def form_valid(self, form):
        # 将当前用户设为创建者；如需默认加入参与者，也可将其加入 attendees
        form.instance.creator = self.request.user
        return super().form_valid(form)
