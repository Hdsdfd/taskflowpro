from django.urls import path
from . import views

app_name = 'calendars'

urlpatterns = [
    path('', views.calendarsEventListView.as_view(), name='event_list'),
    path('<int:pk>/', views.calendarsEventDetailView.as_view(), name='event_detail'),
    path('create/', views.calendarsEventCreateView.as_view(), name='event_create'),
]
