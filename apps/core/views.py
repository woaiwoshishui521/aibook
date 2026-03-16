from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from .pagination import StandardPagination


class BaseListView(generics.ListCreateAPIView):
    """基础列表视图"""
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    @extend_schema(summary='列表查询', description='获取资源列表')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(summary='创建资源', description='创建新资源')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class BaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """基础详情视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(summary='获取详情', description='获取单个资源详情')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(summary='更新资源', description='更新资源信息')
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(summary='部分更新', description='部分更新资源信息')
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(summary='删除资源', description='删除资源')
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
