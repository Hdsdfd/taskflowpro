from django.urls import path
from . import views

app_name = 'calendar'

urlpatterns = [
    path('', views.CalendarEventListView.as_view(), name='event_list'),
    path('<int:pk>/', views.CalendarEventDetailView.as_view(), name='event_detail'),
    path('create/', views.CalendarEventCreateView.as_view(), name='event_create'),
]
