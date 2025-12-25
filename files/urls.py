from django.urls import path
from . import views

app_name = 'files'

urlpatterns = [
    # 文件列表/详情/上传
    path('', views.ProjectFileListView.as_view(), name='file_list'),
    path('<int:pk>/', views.ProjectFileDetailView.as_view(), name='file_detail'),
    path('create/', views.ProjectFileCreateView.as_view(), name='file_create'),
]
