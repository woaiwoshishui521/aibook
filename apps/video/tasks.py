"""
Celery tasks for video compression
"""
from celery import shared_task
from apps.video.services import VideoCompressionService
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_video_compression_task(self, task_id):
    """
    异步处理视频压缩任务
    
    Args:
        task_id: VideoCompressionTask 的 ID
        
    Returns:
        dict: 压缩结果信息
    """
    from apps.video.models import VideoCompressionTask
    
    try:
        # 获取任务对象
        task = VideoCompressionTask.objects.get(id=task_id)
        
        logger.info(f"开始处理视频压缩任务: {task_id} - {task.title}")
        
        # 执行压缩
        result = VideoCompressionService.process_compression_task(task)
        
        logger.info(f"视频压缩任务完成: {task_id} - {task.title}")
        
        return {
            'task_id': task_id,
            'status': 'success',
            'result': result
        }
        
    except VideoCompressionTask.DoesNotExist:
        logger.error(f"视频压缩任务不存在: {task_id}")
        return {
            'task_id': task_id,
            'status': 'error',
            'error': '任务不存在'
        }
        
    except Exception as e:
        logger.error(f"视频压缩任务失败: {task_id} - {str(e)}")
        
        # 重试机制
        try:
            raise self.retry(exc=e, countdown=60)  # 60秒后重试
        except self.MaxRetriesExceededError:
            logger.error(f"视频压缩任务达到最大重试次数: {task_id}")
            return {
                'task_id': task_id,
                'status': 'error',
                'error': str(e)
            }
