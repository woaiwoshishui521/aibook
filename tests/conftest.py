"""
Pytest 全局配置和Fixtures
"""
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """返回APIClient实例"""
    return APIClient()


@pytest.fixture
def authenticated_client(db, django_user_model):
    """返回已认证的APIClient"""
    client = APIClient()
    user = django_user_model.objects.create_user(
        email='test@test.com',
        username='testuser',
        password='testpass123'
    )
    client.force_authenticate(user=user)
    return client, user
