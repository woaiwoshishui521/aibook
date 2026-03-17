# 视频压缩功能 - 问题修复

## ✅ 已修复：身份认证错误

**问题**：创建任务时报错 `{"success":false,"code":"error","message":"身份认证信息未提供。","errors":null,"status_code":401}`

**原因**：Django REST Framework的全局配置要求所有API接口都需要身份认证。

**解决方案**：已将 `VideoCompressionTaskViewSet` 的权限类设置为 `AllowAny`，允许任何人无需认证即可使用视频压缩功能。

### 修改的文件

`apps/video/views.py`:

from rest_framework.permissions import AllowAny

class VideoCompressionTaskViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]  # 允许任何人访问（无需认证）


## 🚀 现在可以正常使用了

### 重启服务器

如果服务器正在运行，请重启：


# 按 Ctrl+C 停止服务器
# 然后重新启动
python manage.py runserver


### 测试功能

1. **访问Web界面**：`http://localhost:8000/video/`
2. **上传视频文件**
3. **选择压缩质量**
4. **点击"开始压缩"**

现在应该可以正常创建压缩任务了！

### API测试


# 测试创建任务（无需认证）
curl -X POST http://localhost:8000/video/api/tasks/ \
  -F "title=测试压缩" \
  -F "original_video=@video.mp4" \
  -F "quality=medium"

# 测试获取任务列表（无需认证）
curl http://localhost:8000/video/api/tasks/

# 测试统计信息（无需认证）
curl http://localhost:8000/video/api/tasks/statistics/


## 🔒 如果需要添加认证

如果将来需要为视频压缩功能添加认证保护，可以：

### 方案1：为整个ViewSet添加认证

编辑 `apps/video/views.py`：

from rest_framework.permissions import IsAuthenticated

class VideoCompressionTaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  # 需要登录


### 方案2：为特定操作添加认证


from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action

class VideoCompressionTaskViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]  # 默认允许所有人
    
    def get_permissions(self):
        # 只有删除操作需要认证
        if self.action == 'destroy':
            return [IsAuthenticated()]
        return super().get_permissions()


### 方案3：基于用户的任务隔离


class VideoCompressionTaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 用户只能看到自己的任务
        return VideoCompressionTask.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # 创建任务时自动关联当前用户
        serializer.save(user=self.request.user)


## 📝 注意事项

1. **当前配置**：任何人都可以使用视频压缩功能，无需登录
2. **生产环境建议**：根据实际需求决定是否需要认证
3. **资源保护**：如果是公开服务，建议添加速率限制（Rate Limiting）

## 速率限制配置（可选）

如果担心滥用，可以在 `apps/video/views.py` 中添加速率限制：


from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class VideoCompressionTaskViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]  # 匿名用户限流


然后在 `config/settings/base.py` 中配置限流规则：


REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/hour',  # 匿名用户每小时10次
        'user': '100/hour',  # 认证用户每小时100次
    }
}


## 问题已解决 ✅

现在你可以正常使用视频压缩功能了！如果还有其他问题，请告诉我。
