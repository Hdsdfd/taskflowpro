from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Comment, CommentLike
from .forms import CommentForm
from tasks.models import Task

@login_required
def add_comment(request, task_id):
    """
    为任务添加评论
    """
    task = get_object_or_404(Task, id=task_id)
    
    # 检查用户是否有权限查看该任务
    if not request.user.is_authenticated:
        messages.error(request, '请先登录')
        return redirect('users:login')
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save() 
            messages.success(request, '评论添加成功')
            return redirect('tasks:task_detail', pk=task_id)
    else:
        form = CommentForm()
    
    return render(request, 'comments/add_comment.html', {
        'form': form,
        'task': task
    })

@login_required
def edit_comment(request, comment_id):
    """
    编辑评论
    """
    comment = get_object_or_404(Comment, id=comment_id)
    
    # 检查用户是否有权限编辑该评论
    if comment.author != request.user:
        messages.error(request, '您没有权限编辑此评论')
        return redirect('tasks:task_detail', pk=comment.task.id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, '评论更新成功')
            return redirect('tasks:task_detail', pk=comment.task.id)
    else:
        form = CommentForm(instance=comment)
    
    return render(request, 'comments/edit_comment.html', {
        'form': form,
        'comment': comment,
        'task': comment.task
    })

@login_required
@require_POST
def delete_comment(request, comment_id):
    """
    删除评论
    """
    comment = get_object_or_404(Comment, id=comment_id)
    
    # 检查用户是否有权限删除该评论
    if comment.author != request.user:
        messages.error(request, '您没有权限删除此评论')
        return redirect('tasks:task_detail', pk=comment.task.id)
    
    task_id = comment.task.id
    comment.delete()
    messages.success(request, '评论删除成功')
    return redirect('tasks:task_detail', pk=task_id)

@login_required
@require_POST
def like_comment(request, comment_id):
    """
    点赞或取消点赞评论（AJAX）
    """
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user
    liked = False
    like_obj = CommentLike.objects.filter(comment=comment, user=user).first()
    if like_obj:
        like_obj.delete()
    else:
        CommentLike.objects.create(comment=comment, user=user)
        liked = True
    return JsonResponse({'success': True, 'liked': liked, 'like_count': comment.like_count})

@login_required
def reply_comment(request, task_id, parent_id):
    """
    回复评论
    """
    task = get_object_or_404(Task, id=task_id)
    parent = get_object_or_404(Comment, id=parent_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.parent = parent
            comment.save()
            messages.success(request, '回复成功')
            return redirect('tasks:task_detail', pk=task_id)
    else:
        form = CommentForm()
    return render(request, 'comments/reply_comment.html', {'form': form, 'task': task, 'parent': parent})

# 修改comment_list接口，递归返回嵌套评论结构
def build_comment_tree(comments, user):
    tree = []
    for comment in comments:
        item = {
            'id': comment.id,
            'author': comment.author.username,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
            'like_count': comment.like_count,
            'liked': comment.likes.filter(user=user).exists(),
            'can_edit': comment.author == user,
            'can_delete': comment.author == user,
            'replies': build_comment_tree(comment.replies.all(), user)
        }
        tree.append(item)
    return tree
    
@login_required
def comment_list(request, task_id):
    """
    获取任务的评论树（用于AJAX请求）
    """
    task = get_object_or_404(Task, id=task_id)
    root_comments = task.comments.filter(parent__isnull=True)
    comment_tree = build_comment_tree(root_comments, request.user)
    return JsonResponse({'comments': comment_tree})

@login_required
def comment_like(request, comment_id):
    """ 
    点赞评论（AJAX） 
    """
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user
    liked = False
    like_obj = CommentLike.objects.filter(comment=comment, user=user).first()
    if like_obj:
        like_obj.delete()