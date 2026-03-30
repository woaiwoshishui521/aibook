"""
Celery tasks for image compression
"""
from celery import shared_task
from apps.image.services import ImageCompressionService
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_image_compression_task(self, task_id):
    """
    异步处理图片压缩任务
    
    Args:
        task_id: ImageCompressionTask 的 ID
        
    Returns:
        dict: 压缩结果信息
    """
    from apps.image.models import ImageCompressionTask
    
    try:
        # 获取任务对象
        task = ImageCompressionTask.objects.get(id=task_id)
        
        logger.info(f"开始处理图片压缩任务: {task_id} - {task.title}")
        
        # 执行压缩
        result = ImageCompressionService.process_compression_task(task)
        
        logger.info(f"图片压缩任务完成: {task_id} - {task.title}")
        
        return {
            'task_id': task_id,
            'status': 'success',
            'result': result
        }
        
    except ImageCompressionTask.DoesNotExist:
        logger.error(f"图片压缩任务不存在: {task_id}")
        return {
            'task_id': task_id,
            'status': 'error',
            'error': '任务不存在'
        }
        
    except Exception as e:
        logger.error(f"图片压缩任务失败: {task_id} - {str(e)}")
        
        # 重试机制
        try:
            raise self.retry(exc=e, countdown=60)  # 60秒后重试
        except self.MaxRetriesExceededError:
            logger.error(f"图片压缩任务达到最大重试次数: {task_id}")
            return {
                'task_id': task_id,
                'status': 'error',
                'error': str(e)
            }
