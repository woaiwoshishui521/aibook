"""
用户模块测试
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.users.models import UserProfile

User = get_user_model()


@pytest.fixture
def api_client():
    """API客户端"""
    return APIClient()


@pytest.fixture
def user_data():
    """用户测试数据"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPass123!',
        'password_confirm': 'TestPass123!',
        'phone': '13800138000'
    }


@pytest.fixture
def create_user(user_data):
    """创建测试用户"""
    data = user_data.copy()
    data.pop('password_confirm')
    user = User.objects.create_user(**data)
    UserProfile.objects.create(user=user)
    return user


@pytest.fixture
def authenticated_client(api_client, create_user):
    """已认证的客户端"""
    api_client.force_authenticate(user=create_user)
    return api_client


@pytest.mark.django_db
class TestUserRegistration:
    """用户注册测试"""
    
    def test_register_success(self, api_client, user_data):
        """测试成功注册"""
        url = reverse('register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email=user_data['email']).exists()
    
    def test_register_password_mismatch(self, api_client, user_data):
        """测试密码不匹配"""
        user_data['password_confirm'] = 'DifferentPass123!'
        url = reverse('register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_duplicate_email(self, api_client, user_data, create_user):
        """测试重复邮箱"""
        url = reverse('register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogin:
    """用户登录测试"""
    
    def test_login_success(self, api_client, create_user, user_data):
        """测试成功登录"""
        url = reverse('login')
        data = {
            'email': user_data['email'],
            'password': user_data['password']
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_login_invalid_credentials(self, api_client, user_data):
        """测试无效凭证"""
        url = reverse('login')
        data = {
            'email': user_data['email'],
            'password': 'wrongpassword'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserProfile:
    """用户资料测试"""
    
    def test_get_profile(self, authenticated_client):
        """测试获取用户资料"""
        url = reverse('profile')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'email' in response.data
    
    def test_update_profile(self, authenticated_client):
        """测试更新用户资料"""
        url = reverse('profile')
        data = {
            'username': 'updated_name',
            'bio': 'Updated bio'
        }
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'updated_name'


@pytest.mark.django_db
class TestChangePassword:
    """修改密码测试"""
    
    def test_change_password_success(self, authenticated_client, user_data):
        """测试成功修改密码"""
        url = reverse('change-password')
        data = {
            'old_password': user_data['password'],
            'new_password': 'NewPass123!',
            'new_password_confirm': 'NewPass123!'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_change_password_wrong_old(self, authenticated_client):
        """测试旧密码错误"""
        url = reverse('change-password')
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'NewPass123!',
            'new_password_confirm': 'NewPass123!'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
