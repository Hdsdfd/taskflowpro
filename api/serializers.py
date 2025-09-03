from rest_framework import serializers
from django.contrib.auth.models import User
from projects.models import Project, Milestone, ProjectTemplate
from tasks.models import Task, TaskTag, TaskDependency, TimeEntry
from files.models import ProjectFile, FileCategory
from notifications.models import Notification, UserNotificationSettings
from analytics.models import ProjectReport, TeamPerformance
from workflows.models import WorkflowInstance, ApprovalRequest
from calendar.models import CalendarEvent, Meeting

class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class ProjectSerializer(serializers.ModelSerializer):
    """项目序列化器"""
    owner = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    
    class Meta:
        model = Project
        fields = '__all__'

class MilestoneSerializer(serializers.ModelSerializer):
    """里程碑序列化器"""
    project = ProjectSerializer(read_only=True)
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Milestone
        fields = '__all__'

class TaskTagSerializer(serializers.ModelSerializer):
    """任务标签序列化器"""
    class Meta:
        model = TaskTag
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    """任务序列化器"""
    project = ProjectSerializer(read_only=True)
    assignee = UserSerializer(read_only=True)
    creator = UserSerializer(read_only=True)
    tags = TaskTagSerializer(many=True, read_only=True)
    is_overdue = serializers.ReadOnlyField()
    days_until_due = serializers.ReadOnlyField()
    has_subtasks = serializers.ReadOnlyField()
    subtask_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = '__all__'

class TaskDependencySerializer(serializers.ModelSerializer):
    """任务依赖序列化器"""
    dependent_task = TaskSerializer(read_only=True)
    prerequisite_task = TaskSerializer(read_only=True)
    
    class Meta:
        model = TaskDependency
        fields = '__all__'

class TimeEntrySerializer(serializers.ModelSerializer):
    """工时记录序列化器"""
    task = TaskSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TimeEntry
        fields = '__all__'

class FileCategorySerializer(serializers.ModelSerializer):
    """文件分类序列化器"""
    class Meta:
        model = FileCategory
        fields = '__all__'

class ProjectFileSerializer(serializers.ModelSerializer):
    """项目文件序列化器"""
    project = ProjectSerializer(read_only=True)
    task = TaskSerializer(read_only=True)
    category = FileCategorySerializer(read_only=True)
    uploaded_by = UserSerializer(read_only=True)
    file_size_mb = serializers.ReadOnlyField()
    file_extension = serializers.ReadOnlyField()
    
    class Meta:
        model = ProjectFile
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    """通知序列化器"""
    recipient = UserSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = '__all__'

class UserNotificationSettingsSerializer(serializers.ModelSerializer):
    """用户通知设置序列化器"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserNotificationSettings
        fields = '__all__'

class ProjectReportSerializer(serializers.ModelSerializer):
    """项目报告序列化器"""
    project = ProjectSerializer(read_only=True)
    generated_by = UserSerializer(read_only=True)
    
    class Meta:
        model = ProjectReport
        fields = '__all__'

class TeamPerformanceSerializer(serializers.ModelSerializer):
    """团队绩效序列化器"""
    user = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    efficiency_rate = serializers.ReadOnlyField()
    time_variance = serializers.ReadOnlyField()
    
    class Meta:
        model = TeamPerformance
        fields = '__all__'

class WorkflowInstanceSerializer(serializers.ModelSerializer):
    """工作流实例序列化器"""
    workflow = serializers.PrimaryKeyRelatedField(read_only=True)
    project = ProjectSerializer(read_only=True)
    task = TaskSerializer(read_only=True)
    started_by = UserSerializer(read_only=True)
    duration = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = WorkflowInstance
        fields = '__all__'

class ApprovalRequestSerializer(serializers.ModelSerializer):
    """审批请求序列化器"""
    requester = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    task = TaskSerializer(read_only=True)
    workflow_instance = WorkflowInstanceSerializer(read_only=True)
    is_overdue = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    
    class Meta:
        model = ApprovalRequest
        fields = '__all__'

class CalendarEventSerializer(serializers.ModelSerializer):
    """日历事件序列化器"""
    creator = UserSerializer(read_only=True)
    attendees = UserSerializer(many=True, read_only=True)
    project = ProjectSerializer(read_only=True)
    task = TaskSerializer(read_only=True)
    duration = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    is_ongoing = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    
    class Meta:
        model = CalendarEvent
        fields = '__all__'

class MeetingSerializer(serializers.ModelSerializer):
    """会议序列化器"""
    organizer = UserSerializer(read_only=True)
    attendees = UserSerializer(many=True, read_only=True)
    required_attendees = UserSerializer(many=True, read_only=True)
    project = ProjectSerializer(read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    is_ongoing = serializers.ReadOnlyField()
    attendee_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Meeting
        fields = '__all__'

# 简化的序列化器，用于嵌套关系
class SimpleProjectSerializer(serializers.ModelSerializer):
    """简化项目序列化器"""
    class Meta:
        model = Project
        fields = ['id', 'name', 'status', 'progress']

class SimpleTaskSerializer(serializers.ModelSerializer):
    """简化任务序列化器"""
    class Meta:
        model = Task
        fields = ['id', 'title', 'status', 'priority', 'due_date']

class SimpleUserSerializer(serializers.ModelSerializer):
    """简化用户序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']
