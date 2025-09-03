from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from projects.models import Project
from tasks.models import Task

class WorkflowTemplate(models.Model):
    """
    工作流模板模型
    """
    name = models.CharField(max_length=200, verbose_name='工作流名称')
    description = models.TextField(blank=True, verbose_name='工作流描述')
    category = models.CharField(
        max_length=50,
        choices=[
            ('task_approval', '任务审批'),
            ('project_approval', '项目审批'),
            ('change_request', '变更请求'),
            ('issue_management', '问题管理'),
            ('release_management', '发布管理'),
            ('custom', '自定义'),
        ],
        default='custom',
        verbose_name='工作流类别'
    )
    
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '工作流模板'
        verbose_name_plural = '工作流模板'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class WorkflowStep(models.Model):
    """
    工作流步骤模型
    """
    STEP_TYPES = (
        ('approval', '审批'),
        ('review', '审核'),
        ('notification', '通知'),
        ('action', '操作'),
        ('condition', '条件判断'),
    )
    
    workflow = models.ForeignKey(WorkflowTemplate, on_delete=models.CASCADE, related_name='steps', verbose_name='工作流')
    name = models.CharField(max_length=200, verbose_name='步骤名称')
    step_type = models.CharField(max_length=20, choices=STEP_TYPES, verbose_name='步骤类型')
    order = models.IntegerField(verbose_name='步骤顺序')
    
    # 审批人设置
    approver_type = models.CharField(
        max_length=20,
        choices=[
            ('specific_user', '指定用户'),
            ('role_based', '基于角色'),
            ('project_owner', '项目负责人'),
            ('task_assignee', '任务负责人'),
            ('any_member', '任意成员'),
        ],
        default='specific_user',
        verbose_name='审批人类型'
    )
    approvers = models.ManyToManyField(User, blank=True, related_name='workflow_steps', verbose_name='审批人')
    
    # 步骤配置
    config = models.JSONField(default=dict, verbose_name='步骤配置')
    is_required = models.BooleanField(default=True, verbose_name='是否必需')
    timeout_hours = models.IntegerField(default=72, verbose_name='超时时间(小时)')
    
    class Meta:
        verbose_name = '工作流步骤'
        verbose_name_plural = '工作流步骤'
        ordering = ['workflow', 'order']
        unique_together = ('workflow', 'order')
    
    def __str__(self):
        return f"{self.workflow.name} - {self.name}"

class WorkflowInstance(models.Model):
    """
    工作流实例模型
    """
    STATUS_CHOICES = (
        ('running', '运行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('error', '错误'),
    )
    
    workflow = models.ForeignKey(WorkflowTemplate, on_delete=models.CASCADE, related_name='instances', verbose_name='工作流模板')
    name = models.CharField(max_length=200, verbose_name='实例名称')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running', verbose_name='状态')
    
    # 关联对象
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='workflows', verbose_name='关联项目')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='workflows', verbose_name='关联任务')
    
    # 实例信息
    current_step = models.ForeignKey(WorkflowStep, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='当前步骤')
    started_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='发起者')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    # 结果
    result = models.CharField(
        max_length=20,
        choices=[
            ('approved', '已批准'),
            ('rejected', '已拒绝'),
            ('cancelled', '已取消'),
            ('error', '错误'),
        ],
        null=True,
        blank=True,
        verbose_name='工作流结果'
        
    )
    notes = models.TextField(blank=True, verbose_name='备注')
    
    class Meta:
        verbose_name = '工作流实例'
        verbose_name_plural = '工作流实例'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    @property
    def duration(self):
        """工作流持续时间"""
        if self.completed_at:
            return self.completed_at - self.started_at
        return timezone.now() - self.started_at
    
    @property
    def is_overdue(self):
        """是否超时"""
        if self.current_step and self.current_step.timeout_hours:
            step_start = self.step_instances.filter(step=self.current_step).first()
            if step_start:
                timeout = step_start.started_at + timezone.timedelta(hours=self.current_step.timeout_hours)
                return timezone.now() > timeout
        return False

class WorkflowStepInstance(models.Model):
    """
    工作流步骤实例模型
    """
    STATUS_CHOICES = (
        ('pending', '等待中'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('skipped', '已跳过'),
        ('error', '错误'),
    )
    
    workflow_instance = models.ForeignKey(WorkflowInstance, on_delete=models.CASCADE, related_name='step_instances', verbose_name='工作流实例')
    step = models.ForeignKey(WorkflowStep, on_delete=models.CASCADE, verbose_name='工作流步骤')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    
    # 执行信息
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='分配给')
    
    # 结果
    result = models.CharField(
        max_length=20,
        choices=[
            ('approved', '已批准'),
            ('rejected', '已拒绝'),
            ('skipped', '已跳过'),
            ('error', '错误'),
        ],
        null=True,
        blank=True,
        verbose_name='步骤结果'
    )
    comments = models.TextField(blank=True, verbose_name='审批意见')
    
    class Meta:
        verbose_name = '工作流步骤实例'
        verbose_name_plural = '工作流步骤实例'
        ordering = ['workflow_instance', 'step__order']
    
    def __str__(self):
        return f"{self.workflow_instance.name} - {self.step.name} ({self.get_status_display()})"
    
    @property
    def duration(self):
        """步骤持续时间"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return timezone.now() - self.started_at
        return None

class ApprovalRequest(models.Model):
    """
    审批请求模型
    """
    PRIORITY_CHOICES = (
        ('low', '低'),
        ('normal', '普通'),
        ('high', '高'),
        ('urgent', '紧急'),
    )
    
    title = models.CharField(max_length=200, verbose_name='审批标题')
    description = models.TextField(verbose_name='审批描述')
    request_type = models.CharField(
        max_length=50,
        choices=[
            ('task_creation', '任务创建'),
            ('task_modification', '任务修改'),
            ('project_change', '项目变更'),
            ('budget_adjustment', '预算调整'),
            ('resource_allocation', '资源分配'),
            ('custom', '自定义'),
        ],
        verbose_name='审批类型'
    )
    
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal', verbose_name='优先级')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approval_requests', verbose_name='申请人')
    
    # 关联对象
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='approval_requests', verbose_name='关联项目')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='approval_requests', verbose_name='关联任务')
    
    # 审批流程
    workflow_instance = models.ForeignKey(WorkflowInstance, on_delete=models.CASCADE, null=True, blank=True, related_name='approval_requests', verbose_name='工作流实例')
    
    # 状态
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', '草稿'),
            ('submitted', '已提交'),
            ('under_review', '审核中'),
            ('approved', '已批准'),
            ('rejected', '已拒绝'),
            ('cancelled', '已取消'),
        ],
        default='draft',
        verbose_name='审批状态'
    )
    
    # 时间信息
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name='提交时间')
    deadline = models.DateTimeField(null=True, blank=True, verbose_name='截止时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    # 附件和备注
    attachments = models.JSONField(default=list, verbose_name='附件信息')
    notes = models.TextField(blank=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '审批请求'
        verbose_name_plural = '审批请求'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_overdue(self):
        """是否逾期"""
        if self.deadline and self.status not in ['approved', 'rejected', 'cancelled']:
            return timezone.now() > self.deadline
        return False
    
    @property
    def days_remaining(self):
        """剩余天数"""
        if self.deadline and self.status not in ['approved', 'rejected', 'cancelled']:
            delta = self.deadline - timezone.now()
            return delta.days
        return None
