from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.ProjectReportListView.as_view(), name='report_list'),
    path('<int:pk>/', views.ProjectReportDetailView.as_view(), name='report_detail'),
    path('create/', views.ProjectReportCreateView.as_view(), name='report_create'),
]
