from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # 账号注册/登录/注销
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # 用户资料与仪表板
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('apply_admin/', views.apply_admin_view, name='apply_admin'),
    # 找回密码
    path('password/forgot/', views.forgot_password_request_view, name='forgot_password'),
    path('password/confirm/', views.forgot_password_confirm_view, name='forgot_password_confirm'),
] 