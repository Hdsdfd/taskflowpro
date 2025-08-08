from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('add/<int:task_id>/', views.add_comment, name='add_comment'),
    path('edit/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('list/<int:task_id>/', views.comment_list, name='comment_list'),
    path('like/<int:comment_id>/', views.like_comment, name='like_comment'),
    path('reply/<int:task_id>/<int:parent_id>/', views.reply_comment, name='reply_comment'),
] 