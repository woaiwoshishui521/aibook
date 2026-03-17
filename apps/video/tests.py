import os
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.video.models import VideoCompressionTask
from apps.video.services import VideoCompressionService


class VideoCompressionTaskModelTest(TestCase):
    """视频压缩任务模型测试"""

    def setUp(self):
        """测试前准备"""
        self.video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"file_content",
            content_type="video/mp4"
        )

    def test_create_task(self):
        """测试创建任务"""
        task = VideoCompressionTask.objects.create(
            title="测试任务",
            original_video=self.video_file,
            quality="medium"
        )

        self.assertEqual(task.title, "测试任务")
        self.assertEqual(task.quality, "medium")
        self.assertEqual(task.status, "pending")
        self.assertEqual(task.progress, 0)

    def test_task_status_choices(self):
        """测试任务状态选项"""
        task = VideoCompressionTask.objects.create(
            title="测试任务",
            original_video=self.video_file,
            quality="high"
        )

        # 测试状态变更
        task.status = 'processing'
        task.save()
        self.assertEqual(task.status, 'processing')

        task.status = 'completed'
        task.save()
        self.assertEqual(task.status, 'completed')

    def test_compression_percentage_calculation(self):
        """测试压缩百分比计算"""
        task = VideoCompressionTask.objects.create(
            title="测试任务",
            original_video=self.video_file,
            quality="medium",
            original_size=1000000,
            compressed_size=500000,
            compression_ratio=0.5
        )

        percentage = task.get_compression_percentage()
        self.assertEqual(percentage, 50.0)

    def test_file_size_mb_methods(self):
        """测试文件大小MB转换方法"""
        task = VideoCompressionTask.objects.create(
            title="测试任务",
            original_video=self.video_file,
            quality="low",
            original_size=10485760,  # 10 MB
            compressed_size=5242880   # 5 MB
        )

        self.assertEqual(task.get_original_size_mb(), 10.0)
        self.assertEqual(task.get_compressed_size_mb(), 5.0)


class VideoCompressionServiceTest(TestCase):
    """视频压缩服务测试"""

    def test_quality_presets(self):
        """测试质量预设"""
        self.assertIn('low', VideoCompressionService.QUALITY_PRESETS)
        self.assertIn('medium', VideoCompressionService.QUALITY_PRESETS)
        self.assertIn('high', VideoCompressionService.QUALITY_PRESETS)

        # 检查预设参数
        low_preset = VideoCompressionService.QUALITY_PRESETS['low']
        self.assertEqual(low_preset['resolution'], '854x480')
        self.assertEqual(low_preset['bitrate'], '500k')
        self.assertEqual(low_preset['fps'], 24)

    def test_quality_preset_values(self):
        """测试不同质量预设的值"""
        presets = VideoCompressionService.QUALITY_PRESETS

        # 低质量
        self.assertEqual(presets['low']['resolution'], '854x480')
        self.assertEqual(presets['low']['bitrate'], '500k')

        # 中等质量
        self.assertEqual(presets['medium']['resolution'], '1280x720')
        self.assertEqual(presets['medium']['bitrate'], '1000k')

        # 高质量
        self.assertEqual(presets['high']['resolution'], '1920x1080')
        self.assertEqual(presets['high']['bitrate'], '2000k')


class VideoCompressionAPITest(TestCase):
    """视频压缩API测试"""

    def setUp(self):
        """测试前准备"""
        self.video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"file_content" * 1000,  # 创建一个较大的文件
            content_type="video/mp4"
        )

    def test_create_compression_task_api(self):
        """测试创建压缩任务API"""
        response = self.client.post('/video/api/tasks/', {
            'title': 'API测试任务',
            'original_video': self.video_file,
            'quality': 'medium'
        })

        # 由于需要认证，可能返回401或403
        # 这里只测试API端点是否存在
        self.assertIn(response.status_code, [201, 401, 403])

    def test_list_tasks_api(self):
        """测试获取任务列表API"""
        response = self.client.get('/video/api/tasks/')

        # 测试API端点是否存在
        self.assertIn(response.status_code, [200, 401, 403])

    def test_statistics_api(self):
        """测试统计信息API"""
        response = self.client.get('/video/api/tasks/statistics/')

        # 测试API端点是否存在
        self.assertIn(response.status_code, [200, 401, 403])


class VideoCompressionPageTest(TestCase):
    """视频压缩页面测试"""

    def test_compression_page_loads(self):
        """测试压缩页面是否加载"""
        response = self.client.get('/video/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '视频压缩工具')
        self.assertContains(response, '上传视频')
