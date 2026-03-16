from django.urls import path
from . import views

urlpatterns = [
    # 认证
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('refresh/', views.TokenRefreshView.as_view(), name='token-refresh'),
    
    # 用户管理
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    
    # 管理员接口
    path('users/', views.UserListView.as_view(), name='user-list'),
]
