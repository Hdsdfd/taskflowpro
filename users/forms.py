from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationForm(UserCreationForm):
    """
    用户注册表单
    """
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': '请输入邮箱'
    }))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请输入用户名'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请输入密码'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请确认密码'
        })
        
        # 自定义错误信息
        self.fields['username'].help_text = '用户名只能包含字母、数字和下划线'
        self.fields['password1'].help_text = '密码至少8位，包含字母和数字'
        self.fields['password2'].help_text = '请再次输入密码确认'

class UserLoginForm(AuthenticationForm):
    """
    用户登录表单
    """
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '请输入用户名'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': '请输入密码'
    }))

class UserProfileForm(forms.ModelForm):
    """
    用户档案编辑表单
    """
    class Meta:
        model = UserProfile
        fields = ('avatar', 'bio')
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请输入个人简介'
            }),
        } 

class AdminApplyForm(forms.Form):
    answer = forms.CharField(label='管理员申请问题：公司创始人是谁？', max_length=100)


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label='邮箱', widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': '请输入注册邮箱'
    }))

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱未注册')
        return email


class PasswordResetConfirmForm(SetPasswordForm):
    code = forms.CharField(label='邮箱验证码', max_length=6, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '请输入6位数字验证码'
    }))

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请输入新密码'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请确认新密码'
        })
        self.fields['code'].widget.attrs.update({
            'class': 'form-control'
        }) 