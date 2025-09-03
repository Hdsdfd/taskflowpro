from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from projects.models import Project, Milestone
from tasks.models import Task, TaskTag, TimeEntry
from files.models import ProjectFile, FileCategory
from notifications.models import Notification, UserNotificationSettings
from analytics.models import ProjectReport, TeamPerformance
from workflows.models import WorkflowInstance, ApprovalRequest
from calendar.models import CalendarEvent, Meeting
from .serializers import (
    UserSerializer, ProjectSerializer, MilestoneSerializer,
    TaskSerializer, TaskTagSerializer, TimeEntrySerializer,
    ProjectFileSerializer, FileCategorySerializer,
    NotificationSerializer, UserNotificationSettingsSerializer,
    ProjectReportSerializer, TeamPerformanceSerializer,
    WorkflowInstanceSerializer, ApprovalRequestSerializer,
    CalendarEventSerializer, MeetingSerializer
)
from django.db import models
from django.utils import timezone

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """用户视图集"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def projects(self, request, pk=None):
        """获取用户参与的项目"""
        user = self.get_object()
        projects = user.projects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """获取用户的任务"""
        user = self.get_object()
        tasks = user.assigned_tasks.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

class ProjectViewSet(viewsets.ModelViewSet):
    """项目视图集"""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """根据用户权限过滤项目"""
        user = self.request.user
        if user.is_staff:
            return Project.objects.all()
        return user.projects.all()
    
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """获取项目任务"""
        project = self.get_object()
        tasks = project.tasks.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """获取项目成员"""
        project = self.get_object()
        members = project.members.all()
        serializer = UserSerializer(members, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """添加项目成员"""
        project = self.get_object()
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            project.members.add(user)
            return Response({'message': '成员添加成功'})
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_400_BAD_REQUEST)

class TaskViewSet(viewsets.ModelViewSet):
    """任务视图集"""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """根据用户权限过滤任务"""
        user = self.request.user
        if user.is_staff:
            return Task.objects.all()
        return Task.objects.filter(
            models.Q(assignee=user) | 
            models.Q(creator=user) |
            models.Q(project__members=user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def start_timer(self, request, pk=None):
        """开始计时"""
        task = self.get_object()
        user = request.user
        
        # 检查是否已有正在进行的计时
        active_timer = TimeEntry.objects.filter(
            task=task, user=user, end_time__isnull=True
        ).first()
        
        if active_timer:
            return Response({'error': '已有正在进行的计时'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建新的计时记录
        time_entry = TimeEntry.objects.create(
            task=task,
            user=user,
            start_time=timezone.now()
        )
        
        return Response({'message': '计时开始', 'time_entry_id': time_entry.id})
    
    @action(detail=True, methods=['post'])
    def stop_timer(self, request, pk=None):
        """停止计时"""
        task = self.get_object()
        user = request.user
        
        # 查找正在进行的计时
        active_timer = TimeEntry.objects.filter(
            task=task, user=user, end_time__isnull=True
        ).first()
        
        if not active_timer:
            return Response({'error': '没有正在进行的计时'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 停止计时
        active_timer.end_time = timezone.now()
        active_timer.save()
        
        return Response({'message': '计时停止', 'duration': active_timer.duration_hours})

class ProjectFileViewSet(viewsets.ModelViewSet):
    """项目文件视图集"""
    queryset = ProjectFile.objects.all()
    serializer_class = ProjectFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """根据用户权限过滤文件"""
        user = self.request.user
        if user.is_staff:
            return ProjectFile.objects.all()
        return ProjectFile.objects.filter(
            models.Q(project__members=user) |
            models.Q(uploaded_by=user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        """下载文件"""
        file_obj = self.get_object()
        file_obj.increment_download_count()
        return Response({'message': '下载记录已更新'})

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """通知视图集"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的通知"""
        return self.request.user.notifications.all()
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """标记通知为已读"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'message': '通知已标记为已读'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """标记所有通知为已读"""
        self.get_queryset().update(is_read=True)
        return Response({'message': '所有通知已标记为已读'})

class CalendarEventViewSet(viewsets.ModelViewSet):
    """日历事件视图集"""
    queryset = CalendarEvent.objects.all()
    serializer_class = CalendarEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """根据用户权限过滤事件"""
        user = self.request.user
        return CalendarEvent.objects.filter(
            models.Q(creator=user) |
            models.Q(attendees=user) |
            models.Q(project__members=user)
        ).distinct()
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """获取即将到来的事件"""
        upcoming_events = self.get_queryset().filter(
            start_time__gte=timezone.now()
        ).order_by('start_time')[:10]
        serializer = self.get_serializer(upcoming_events, many=True)
        return Response(serializer.data)

class MeetingViewSet(viewsets.ModelViewSet):
    """会议视图集"""
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """根据用户权限过滤会议"""
        user = self.request.user
        return Meeting.objects.filter(
            models.Q(organizer=user) |
            models.Q(attendees=user) |
            models.Q(required_attendees=user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """加入会议"""
        meeting = self.get_object()
        user = request.user
        
        if user not in meeting.attendees.all():
            meeting.attendees.add(user)
            return Response({'message': '已加入会议'})
        else:
            return Response({'message': '您已经是会议参与者'})
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """离开会议"""
        meeting = self.get_object()
        user = request.user
        
        if user in meeting.attendees.all():
            meeting.attendees.remove(user)
            return Response({'message': '已离开会议'})
        else:
            return Response({'message': '您不是会议参与者'})

class DashboardViewSet(viewsets.ViewSet):
    """仪表板视图集"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """获取仪表板概览数据"""
        user = request.user
        
        # 项目统计
        total_projects = user.projects.count()
        active_projects = user.projects.filter(status='active').count()
        
        # 任务统计
        total_tasks = user.assigned_tasks.count()
        completed_tasks = user.assigned_tasks.filter(status='completed').count()
        overdue_tasks = user.assigned_tasks.filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count()
        
        # 通知统计
        unread_notifications = user.notifications.filter(is_read=False).count()
        
        # 即将到期的任务
        upcoming_deadlines = user.assigned_tasks.filter(
            due_date__gte=timezone.now(),
            due_date__lte=timezone.now() + timezone.timedelta(days=7),
            status__in=['pending', 'in_progress']
        ).count()
        
        return Response({
            'projects': {
                'total': total_projects,
                'active': active_projects
            },
            'tasks': {
                'total': total_tasks,
                'completed': completed_tasks,
                'overdue': overdue_tasks,
                'upcoming_deadlines': upcoming_deadlines
            },
            'notifications': {
                'unread': unread_notifications
            }
        })
    
    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """获取最近活动"""
        user = request.user
        
        # 最近的任务更新
        recent_tasks = user.assigned_tasks.order_by('-updated_at')[:5]
        task_serializer = TaskSerializer(recent_tasks, many=True)
        
        # 最近的通知
        recent_notifications = user.notifications.order_by('-created_at')[:5]
        notification_serializer = NotificationSerializer(recent_notifications, many=True)
        
        return Response({
            'recent_tasks': task_serializer.data,
            'recent_notifications': notification_serializer.data
        })
