from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """用户注册"""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary='用户注册',
        description='注册新用户账号',
        responses={
            201: OpenApiResponse(description='注册成功'),
            400: OpenApiResponse(description='参数错误'),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LoginView(TokenObtainPairView):
    """用户登录 - JWT Token"""
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary='用户登录',
        description='使用邮箱和密码登录，返回访问令牌和刷新令牌',
        responses={
            200: OpenApiResponse(description='登录成功'),
            401: OpenApiResponse(description='认证失败'),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutView(TokenBlacklistView):
    """用户登出 - 作废Token"""
    @extend_schema(
        summary='用户登出',
        description='将刷新令牌加入黑名单',
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TokenRefreshView(TokenRefreshView):
    """刷新访问令牌"""
    @extend_schema(
        summary='刷新令牌',
        description='使用刷新令牌获取新的访问令牌',
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """用户个人信息"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer
    
    @extend_schema(
        summary='获取当前用户信息',
        description='获取当前登录用户的详细信息',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary='更新用户信息',
        description='更新当前登录用户的信息',
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class ChangePasswordView(APIView):
    """修改密码"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary='修改密码',
        description='修改当前用户的登录密码',
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(description='修改成功'),
            400: OpenApiResponse(description='参数错误'),
        }
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response(
            {'message': '密码修改成功'},
            status=status.HTTP_200_OK
        )


class UserListView(generics.ListAPIView):
    """用户列表（仅管理员）"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @extend_schema(
        summary='用户列表',
        description='获取所有用户列表（管理员权限）',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
