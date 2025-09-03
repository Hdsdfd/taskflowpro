from django.urls import path
from . import views

app_name = 'workflows'

urlpatterns = [
    path('', views.ApprovalRequestListView.as_view(), name='approval_list'),
    path('<int:pk>/', views.ApprovalRequestDetailView.as_view(), name='approval_detail'),
    path('create/', views.ApprovalRequestCreateView.as_view(), name='approval_create'),
]
