from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import render
from django.http import FileResponse, Http404
from apps.video.models import VideoCompressionTask
from apps.video.serializers import (
    VideoCompressionTaskSerializer,
    VideoCompressionTaskCreateSerializer
)
from apps.video.tasks import process_video_compression_task
import os


class VideoCompressionTaskViewSet(viewsets.ModelViewSet):
    """视频压缩任务视图集"""

    queryset = VideoCompressionTask.objects.all()
    serializer_class = VideoCompressionTaskSerializer
    permission_classes = [AllowAny]  # 允许任何人访问（无需认证）

    def get_serializer_class(self):
        if self.action == 'create':
            return VideoCompressionTaskCreateSerializer
        return VideoCompressionTaskSerializer

    def create(self, request, *args, **kwargs):
        """创建压缩任务并提交到 Celery 队列"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()

        # 使用 Celery 异步处理压缩任务
        process_video_compression_task.delay(task.id)

        # 返回任务信息
        response_serializer = VideoCompressionTaskSerializer(task)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """下载压缩后的视频"""
        task = self.get_object()

        if task.status != 'completed' or not task.compressed_video:
            return Response(
                {'error': '视频还未压缩完成或压缩失败'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            response = FileResponse(
                task.compressed_video.open('rb'),
                content_type='video/mp4'
            )
            response['Content-Disposition'] = f'attachment; filename="{task.compressed_video.name.split("/")[-1]}"'
            return response
        except Exception as e:
            raise Http404("文件不存在")

    @action(detail=True, methods=['get'])
    def stream(self, request, pk=None):
        """流式播放压缩后的视频"""
        task = self.get_object()

        if task.status != 'completed' or not task.compressed_video:
            return Response(
                {'error': '视频还未压缩完成或压缩失败'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            response = FileResponse(
                task.compressed_video.open('rb'),
                content_type='video/mp4'
            )
            # 不设置 Content-Disposition 以便在浏览器中直接播放
            response['Accept-Ranges'] = 'bytes'
            return response
        except Exception as e:
            raise Http404("文件不存在")

    @action(detail=True, methods=['get'])
    def stream_original(self, request, pk=None):
        """流式播放原始视频"""
        task = self.get_object()

        if not task.original_video:
            return Response(
                {'error': '原始视频不存在'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            response = FileResponse(
                task.original_video.open('rb'),
                content_type='video/mp4'
            )
            # 不设置 Content-Disposition 以便在浏览器中直接播放
            response['Accept-Ranges'] = 'bytes'
            return response
        except Exception as e:
            raise Http404("文件不存在")

    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """重试失败的任务"""
        task = self.get_object()

        if task.status not in ['failed', 'completed']:
            return Response(
                {'error': '只能重试失败或已完成的任务'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 重置任务状态
        task.status = 'pending'
        task.progress = 0
        task.error_message = None
        task.save()

        # 使用 Celery 异步处理压缩任务
        process_video_compression_task.delay(task.id)

        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取统计信息"""
        total = VideoCompressionTask.objects.count()
        pending = VideoCompressionTask.objects.filter(status='pending').count()
        processing = VideoCompressionTask.objects.filter(status='processing').count()
        completed = VideoCompressionTask.objects.filter(status='completed').count()
        failed = VideoCompressionTask.objects.filter(status='failed').count()

        # 计算总压缩节省的空间
        completed_tasks = VideoCompressionTask.objects.filter(
            status='completed',
            original_size__isnull=False,
            compressed_size__isnull=False
        )
        total_saved = sum(
            task.original_size - task.compressed_size
            for task in completed_tasks
        )
        total_saved_mb = round(total_saved / (1024 * 1024), 2)

        return Response({
            'total': total,
            'pending': pending,
            'processing': processing,
            'completed': completed,
            'failed': failed,
            'total_saved_mb': total_saved_mb,
        })

    def destroy(self, request, *args, **kwargs):
        """删除任务及其关联的视频文件"""
        task = self.get_object()

        # 删除原始视频文件
        if task.original_video:
            try:
                if os.path.isfile(task.original_video.path):
                    os.remove(task.original_video.path)
            except Exception as e:
                print(f"删除原始视频文件失败: {str(e)}")

        # 删除压缩后的视频文件
        if task.compressed_video:
            try:
                if os.path.isfile(task.compressed_video.path):
                    os.remove(task.compressed_video.path)
            except Exception as e:
                print(f"删除压缩视频文件失败: {str(e)}")

        # 删除数据库记录
        return super().destroy(request, *args, **kwargs)


def video_compression_page(request):
    """视频压缩页面"""
    return render(request, 'video/compression.html')










