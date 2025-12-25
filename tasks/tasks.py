from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Task
from notifications.models import Notification
from projects.models import Project

@shared_task
def send_task_reminder(task_id):
    """发送任务提醒"""
    try:
        task = Task.objects.get(id=task_id)
        if task.status not in ['completed', 'cancelled']:
            # 发送邮件提醒
            subject = f'任务提醒: {task.title}'
            message = f'''
            您好 {task.assignee.first_name or task.assignee.username}，
            
            您有一个任务即将到期：
            
            任务标题: {task.title}
            项目: {task.project.name}
            截止日期: {task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else '无'}
            任务描述: {task.description[:100]}...
            
            请及时处理，避免逾期。
            
            此邮件由系统自动发送，请勿回复。
            '''
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[task.assignee.email],
                fail_silently=False,
            )
            
            # 创建站内通知
            Notification.objects.create(
                recipient=task.assignee,
                notification_type='task_due',
                title=f'任务即将到期: {task.title}',
                message=f'任务 "{task.title}" 即将到期，请及时处理。',
                priority='high'
            )
            
            return f'任务提醒发送成功: {task.title}'
    except Task.DoesNotExist:
        return f'任务不存在: {task_id}'
    except Exception as e:
        return f'发送任务提醒失败: {str(e)}'

@shared_task
def send_overdue_notifications():
    """发送逾期任务通知"""
    overdue_tasks = Task.objects.filter(
        due_date__lt=timezone.now(),
        status__in=['pending', 'in_progress']
    )
    
    for task in overdue_tasks:
        # 创建逾期通知
        Notification.objects.create(
            recipient=task.assignee,
            notification_type='task_overdue',
            title=f'任务已逾期: {task.title}',
            message=f'任务 "{task.title}" 已逾期，请尽快处理。',
            priority='urgent'
        )
    
    return f'发送了 {overdue_tasks.count()} 个逾期通知'

@shared_task
def update_project_progress():
    """更新项目进度"""
    projects = Project.objects.filter(status='active')
    
    for project in projects:
        total_tasks = project.tasks.count()
        if total_tasks > 0:
            completed_tasks = project.tasks.filter(status='completed').count()
            progress = int((completed_tasks / total_tasks) * 100)
            project.progress = progress
            project.save()
    
    return f'更新了 {projects.count()} 个项目的进度'

@shared_task
def cleanup_old_notifications():
    """清理旧通知"""
    cutoff_date = timezone.now() - timedelta(days=90)
    deleted_count = Notification.objects.filter(
        created_at__lt=cutoff_date,
        is_read=True
    ).delete()[0]
    
    return f'清理了 {deleted_count} 个旧通知'

@shared_task
def send_daily_summary():
    """发送每日摘要"""
    from django.contrib.auth.models import User
    
    users = User.objects.filter(is_active=True)
    
    for user in users:
        # 获取用户今日任务统计
        today = timezone.now().date()
        today_tasks = user.assigned_tasks.filter(
            created_at__date=today
        )
        completed_today = today_tasks.filter(status='completed').count()
        total_today = today_tasks.count()
        
        # 获取明日到期任务
        tomorrow = today + timedelta(days=1)
        tomorrow_deadlines = user.assigned_tasks.filter(
            due_date__date=tomorrow,
            status__in=['pending', 'in_progress']
        ).count()
        
        if total_today > 0 or tomorrow_deadlines > 0:
            subject = f'每日摘要 - {today.strftime("%Y-%m-%d")}'
            message = f'''
            您好 {user.first_name or user.username}，
            
            以下是您的今日摘要：
            
            今日完成任务: {completed_today}/{total_today}
            明日到期任务: {tomorrow_deadlines} 个
            
            祝您工作顺利！
            
            此邮件由系统自动发送，请勿回复。
            '''
            
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception:
                pass  # 邮件发送失败不影响其他用户
    
    return f'发送了 {users.count()} 个用户的每日摘要'

@shared_task
def sync_external_data():
    """同步外部数据"""
    # 这里可以添加与第三方系统同步的逻辑
    # 例如：同步Git提交、同步日历事件等
    return '外部数据同步完成'

@shared_task
def generate_reports():
    """生成定期报告"""
    from analytics.models import ProjectReport
    
    # 生成项目进度报告
    active_projects = Project.objects.filter(status='active')
    
    for project in active_projects:
        # 检查是否已有今日报告
        today = timezone.now().date()
        existing_report = ProjectReport.objects.filter(
            project=project,
            report_type='progress',
            period_start=today,
            period_end=today
        ).first()
        
        if not existing_report:
            # 生成新报告
            report_data = {
                'total_tasks': project.task_count,
                'completed_tasks': project.completed_task_count,
                'progress_percentage': project.progress_percentage,
                'overdue_tasks': project.tasks.filter(
                    due_date__lt=timezone.now(),
                    status__in=['pending', 'in_progress']
                ).count()
            }
            
            ProjectReport.objects.create(
                project=project,
                report_type='progress',
                title=f'{project.name} - 进度报告',
                content=report_data,
                generated_by=project.owner,
                period_start=today,
                period_end=today
            )
    
    return f'生成了 {active_projects.count()} 个项目的进度报告'
