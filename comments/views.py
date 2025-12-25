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
    # 逻辑解释：
    # 1) 解析路由参数 task_id，获取目标任务；若不存在返回 404，避免泄露信息。
    # 2) 若是 GET：渲染空表单以供输入。
    # 3) 若是 POST：对输入进行表单校验，合法则落库，并附带作者与任务引用。
    # 4) 成功后跳转任务详情，失败则回显表单错误。
    # 获取任务对象；若不存在则返回 404
    task = get_object_or_404(Task, id=task_id)
    
    # 权限提示：此处 @login_required 已保证登录
    # 若需进一步限制（仅项目成员可评论），可额外判断 task.project.members 是否包含当前用户
    
    if request.method == 'POST':
        # 绑定提交数据到表单
        form = CommentForm(request.POST)
        if form.is_valid():
            # 推迟保存以便补充 task 与 author 字段
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save() 
            messages.success(request, '评论添加成功')
            return redirect('tasks:task_detail', pk=task_id)
    else:
        # 初次进入渲染空表单
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
    # 逻辑解释：
    # 1) 基于 comment_id 定位评论。
    # 2) 权限：仅作者本人可编辑，防止越权。
    # 3) 提交时用 instance=comment 保持原对象更新而非创建新对象。
    # 4) 成功后重定向回任务详情。
    # 仅评论作者可编辑
    comment = get_object_or_404(Comment, id=comment_id)
    
    # 检查用户是否有权限编辑该评论
    if comment.author != request.user:
        messages.error(request, '您没有权限编辑此评论')
        return redirect('tasks:task_detail', pk=comment.task.id)
    
    if request.method == 'POST':
        # 以实例模式编辑
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
    # 逻辑解释：
    # 1) require_POST 防止 CSRF/误点；
    # 2) 权限：仅作者可删；
    # 3) 删除后回到任务详情，提升用户体验。
    # 仅评论作者可删除
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
    # 逻辑解释：
    # 1) 幂等切换：同一用户对同一评论的点赞是可切换的。
    # 2) 使用 first() 获取唯一关系，存在则删除，不存在则创建。
    # 3) 返回 liked 布尔与最新 like_count，用于前端按钮与计数同步。
    # 切换点赞状态：若已点赞则取消，否则添加
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
    # 逻辑解释：
    # 1) 结合父评论与任务形成树结构；
    # 2) 提交表单后同样补齐 author、task 与 parent 字段再保存；
    # 3) 成功后回到任务详情；
    # 4) 若要控制深度，可增加最大层级校验。
    # 绑定父评论与任务形成层级结构
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
    """递归构建嵌套评论结构，返回适合前端渲染的字典列表"""
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
    # 仅返回顶级评论作为根节点，然后递归附带子回复
    task = get_object_or_404(Task, id=task_id)
    root_comments = task.comments.filter(parent__isnull=True)
    comment_tree = build_comment_tree(root_comments, request.user)
    return JsonResponse({'comments': comment_tree})

@login_required
def comment_like(request, comment_id):
    """ 
    点赞评论（AJAX） 
    """
    # 与 like_comment 功能一致：切换点赞状态并返回计数
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