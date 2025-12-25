from django.urls import path
from . import views

app_name = 'integrations'

urlpatterns = [
    path('', views.ThirdPartyServiceListView.as_view(), name='service_list'),
    path('<int:pk>/', views.ThirdPartyServiceDetailView.as_view(), name='service_detail'),
    path('create/', views.ThirdPartyServiceCreateView.as_view(), name='service_create'),
]
