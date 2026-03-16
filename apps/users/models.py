from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class User(AbstractUser):
    """自定义用户模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('邮箱'), unique=True)
    phone = models.CharField(_('手机号'), max_length=15, blank=True)
    avatar = models.ImageField(_('头像'), upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(_('简介'), blank=True)
    
    # 状态字段
    is_active = models.BooleanField(_('是否激活'), default=True)
    is_staff = models.BooleanField(_('是否员工'), default=False)
    is_superuser = models.BooleanField(_('是否超级用户'), default=False)
    
    # 时间戳
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    last_login_ip = models.GenericIPAddressField(_('最后登录IP'), blank=True, null=True)
    
    # 将 email 作为登录字段
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username


class UserProfile(models.Model):
    """用户扩展信息"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile',
        verbose_name=_('用户')
    )
    birth_date = models.DateField(_('生日'), blank=True, null=True)
    gender = models.CharField(
        _('性别'), 
        max_length=10, 
        choices=[
            ('male', _('男')),
            ('female', _('女')),
            ('other', _('其他')),
        ],
        blank=True
    )
    address = models.CharField(_('地址'), max_length=255, blank=True)
    city = models.CharField(_('城市'), max_length=100, blank=True)
    country = models.CharField(_('国家'), max_length=100, blank=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = _('用户资料')
        verbose_name_plural = _('用户资料')
    
    def __str__(self):
        return f"{self.user.email} 的资料"
