from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'milestones', views.MilestoneViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'task-tags', views.TaskTagViewSet)
router.register(r'time-entries', views.TimeEntryViewSet)
router.register(r'files', views.ProjectFileViewSet)
router.register(r'file-categories', views.FileCategoryViewSet)
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'user-notification-settings', views.UserNotificationSettingsViewSet, basename='user-notification-setting')
router.register(r'project-reports', views.ProjectReportViewSet, basename='project-report')
router.register(r'team-performance', views.TeamPerformanceViewSet, basename='team-performance')
router.register(r'workflow-instances', views.WorkflowInstanceViewSet, basename='workflow-instance')
router.register(r'approval-requests', views.ApprovalRequestViewSet, basename='approval-request')
router.register(r'calendar-events', views.CalendarEventViewSet)
router.register(r'meetings', views.MeetingViewSet)
router.register(r'dashboard', views.DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]
