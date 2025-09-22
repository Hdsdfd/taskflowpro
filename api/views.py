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
from calendars.models import calendarsEvent, Meeting
from .serializers import (
    UserSerializer, ProjectSerializer, MilestoneSerializer,
    TaskSerializer, TaskTagSerializer, TimeEntrySerializer,
    ProjectFileSerializer, FileCategorySerializer,
    NotificationSerializer, UserNotificationSettingsSerializer,
    ProjectReportSerializer, TeamPerformanceSerializer,
    WorkflowInstanceSerializer, ApprovalRequestSerializer,
    calendarsEventSerializer, MeetingSerializer
)
from django.db import models
from django.utils import timezone

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """用户视图集"""
    # 逻辑解释：
    # - 只读集合：仅提供查询用户的能力，避免通过 API 修改账号数据。
    # - 衍生动作 projects/tasks 直接读取用户的反向关系，便于前端按用户维度取数据。
    # - 数据范围：默认全量；若需隔离可按组织/租户在 queryset 处扩展。
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def projects(self, request, pk=None):
        """获取用户参与的项目"""
        # 通过路由中的 pk 获取用户，再取反向关系 projects
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
    # 逻辑解释：
    # - 提供完整 CRUD；
    # - get_queryset 做数据级权限控制：staff 全量，普通用户仅返回参与的项目；
    # - 自定义动作 tasks/members 提供便捷子资源查询；
    # - add_member 简化添加成员流程，生产可加入角色校验与审计。
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
        # 简化逻辑：只按 id 添加；生产环境建议校验是否管理员或项目负责人
        project = self.get_object()
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            project.members.add(user)
            return Response({'message': '成员添加成功'})
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_400_BAD_REQUEST)

class MilestoneViewSet(viewsets.ModelViewSet):
    """里程碑视图集"""
    # 逻辑解释：
    # - 与 Project 相同的数据权限模型：staff 全量，其余仅能访问自己参与项目下的里程碑。
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """根据用户权限过滤里程碑"""
        user = self.request.user
        if user.is_staff:
            return Milestone.objects.all()
        return Milestone.objects.filter(project__members=user)

class TaskViewSet(viewsets.ModelViewSet):
    """任务视图集"""
    # 逻辑解释：
    # - 数据权限：管理员全量；普通用户需满足 负责人/创建者/项目成员 任一条件；
    # - start_timer/stop_timer 将计时拆分为开始/停止两个幂等动作，确保一个用户在一个任务上仅有一条活跃计时。
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
        # 业务逻辑：一个用户在同一任务上同一时间仅允许一个进行中的计时
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
        # 补全结束时间后模型会自动计算 duration_hours
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

class TaskTagViewSet(viewsets.ModelViewSet):
    """任务标签视图集"""
    queryset = TaskTag.objects.all()
    serializer_class = TaskTagSerializer
    permission_classes = [permissions.IsAuthenticated]

class TimeEntryViewSet(viewsets.ModelViewSet):
    """工时记录视图集"""
    queryset = TimeEntry.objects.all()
    serializer_class = TimeEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """根据用户权限过滤工时记录"""
        user = self.request.user
        if user.is_staff:
            return TimeEntry.objects.all()
        return TimeEntry.objects.filter(user=user)

class ProjectFileViewSet(viewsets.ModelViewSet):
    """项目文件视图集"""
    # 逻辑解释：
    # - 权限：管理员全量；普通用户需是项目成员或上传者；
    # - download 动作仅记录下载次数，如需实际下载建议返回文件直链或使用 FileResponse。
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
        # 此处仅记录下载次数；实际文件下载需结合文件存储与权限控制
        file_obj = self.get_object()
        file_obj.increment_download_count()
        return Response({'message': '下载记录已更新'})

class FileCategoryViewSet(viewsets.ModelViewSet):
    """文件分类视图集"""
    # 逻辑解释：
    # - 一般由管理员维护分类；若对普通成员开放，建议限制可编辑字段。
    queryset = FileCategory.objects.all()
    serializer_class = FileCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """通知视图集"""
    # 逻辑解释：
    # - 只读：防止用户篡改历史通知；
    # - 数据范围固定到 request.user；
    # - mark_read/mark_all_read 为副作用动作，更新已读状态。
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

class UserNotificationSettingsViewSet(viewsets.ModelViewSet):
    """用户通知设置视图集"""
    # 逻辑解释：
    # - 用户级私有资源：queryset 限定为当前用户；
    # - 允许 CRUD 便于前端偏好设置持久化。
    serializer_class = UserNotificationSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的设置"""
        return UserNotificationSettings.objects.filter(user=self.request.user)

class ProjectReportViewSet(viewsets.ReadOnlyModelViewSet):
    """项目报告视图集"""
    # 逻辑解释：
    # - 只读报表：避免通过 API 改动历史报表记录；
    # - 数据权限：成员或报表生成者可见；
    # - 如需导出，可新增导出动作（CSV/PDF）。
    queryset = ProjectReport.objects.all()
    serializer_class = ProjectReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """根据用户权限过滤报告"""
        user = self.request.user
        if user.is_staff:
            return ProjectReport.objects.all()
        return ProjectReport.objects.filter(
            models.Q(project__members=user) |
            models.Q(generated_by=user)
        ).distinct()

class TeamPerformanceViewSet(viewsets.ReadOnlyModelViewSet):
    """团队绩效视图集"""
    # 逻辑解释：
    # - 只读：防止写入；
    # - 数据范围：仅返回当前用户或与其所在项目相关的数据。
    queryset = TeamPerformance.objects.all()
    serializer_class = TeamPerformanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """根据用户权限过滤绩效数据"""
        user = self.request.user
        if user.is_staff:
            return TeamPerformance.objects.all()
        return TeamPerformance.objects.filter(
            models.Q(user=user) |
            models.Q(project__members=user)
        ).distinct()

class WorkflowInstanceViewSet(viewsets.ModelViewSet):
    """工作流实例视图集"""
    # 逻辑解释：
    # - 可编辑：允许创建/推进/更新实例；
    # - 数据权限：发起人或项目成员可见；
    # - 与审批流结合时可扩展动作（如 approve/reject）。
    queryset = WorkflowInstance.objects.all()
    serializer_class = WorkflowInstanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """根据用户权限过滤工作流"""
        user = self.request.user
        if user.is_staff:
            return WorkflowInstance.objects.all()
        return WorkflowInstance.objects.filter(
            models.Q(started_by=user) |
            models.Q(project__members=user)
        ).distinct()

class ApprovalRequestViewSet(viewsets.ModelViewSet):
    """审批请求视图集"""
    # 逻辑解释：
    # - 可编辑：新建/撤回/更新审批请求；
    # - 数据权限：仅请求者或项目成员可见；
    # - 可新增动作以实现批量审批或加签等高级功能。
    queryset = ApprovalRequest.objects.all()
    serializer_class = ApprovalRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """根据用户权限过滤审批请求"""
        user = self.request.user
        if user.is_staff:
            return ApprovalRequest.objects.all()
        return ApprovalRequest.objects.filter(
            models.Q(requester=user) |
            models.Q(project__members=user)
        ).distinct()

class calendarsEventViewSet(viewsets.ModelViewSet):
    """日历事件视图集"""
    # 逻辑解释：
    # - 可编辑：新建/编辑事件；
    # - 数据权限：仅与用户相关（创建者/参与者/同项目）可见；
    # - upcoming 动作用于首页/仪表板展示未来 10 条。
    queryset = calendarsEvent.objects.all()
    serializer_class = calendarsEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """根据用户权限过滤事件"""
        user = self.request.user
        return calendarsEvent.objects.filter(
            models.Q(creator=user) |
            models.Q(attendees=user) |
            models.Q(project__members=user)
        ).distinct()
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """获取即将到来的事件"""
        # 过滤开始时间在当前之后的记录，并限制返回数量
        upcoming_events = self.get_queryset().filter(
            start_time__gte=timezone.now()
        ).order_by('start_time')[:10]
        serializer = self.get_serializer(upcoming_events, many=True)
        return Response(serializer.data)

class MeetingViewSet(viewsets.ModelViewSet):
    """会议视图集"""
    # 逻辑解释：
    # - 可编辑：新建/编辑会议；
    # - 数据权限：与会者/必要与会者/组织者可见；
    # - join/leave 采用幂等语义，便于前端简单调用。
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
        # 幂等添加：已存在则提示无需重复加入
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
        # 幂等删除：不在列表中则提示无需移除
        meeting = self.get_object()
        user = request.user
        
        if user in meeting.attendees.all():
            meeting.attendees.remove(user)
            return Response({'message': '已离开会议'})
        else:
            return Response({'message': '您不是会议参与者'})

class DashboardViewSet(viewsets.ViewSet):
    """仪表板视图集"""
    # 逻辑解释：
    # - 将多个模型的统计聚合到一个端点，减少前端并发请求；
    # - overview 提供关键 KPI；recent_activity 提供最近动态列表。
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """获取仪表板概览数据"""
        # 汇总项目/任务/通知/即将到期任务等指标
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
        # 返回最近更新的任务与最近的通知，便于首页展示
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
