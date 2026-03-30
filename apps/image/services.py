"""
图片压缩服务
使用 Pillow 进行图片压缩处理
"""
import os
from PIL import Image
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from django.core.files import File
from django.utils import timezone


class ImageCompressionService:
    """图片压缩服务类"""

    # 预设质量配置
    QUALITY_PRESETS = {
        'low': {
            'quality': 60,
            'optimize': True,
        },
        'medium': {
            'quality': 80,
            'optimize': True,
        },
        'high': {
            'quality': 90,
            'optimize': True,
        },
    }

    # 格式映射
    FORMAT_MAPPING = {
        'jpeg': 'JPEG',
        'jpg': 'JPEG',
        'png': 'PNG',
        'webp': 'WEBP',
        'gif': 'GIF',
        'bmp': 'BMP',
        'tiff': 'TIFF',
    }

    @staticmethod
    def get_image_info(image_path: str) -> Dict[str, Any]:
        """
        获取图片信息

        Args:
            image_path: 图片文件路径

        Returns:
            包含图片信息的字典
        """
        try:
            with Image.open(image_path) as img:
                info = {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'size': os.path.getsize(image_path),
                }
                return info
        except Exception as e:
            raise Exception(f"获取图片信息失败: {str(e)}")

    @staticmethod
    def calculate_new_dimensions(
        original_width: int,
        original_height: int,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None
    ) -> Tuple[int, int]:
        """
        计算新的图片尺寸（保持宽高比）

        Args:
            original_width: 原始宽度
            original_height: 原始高度
            max_width: 最大宽度
            max_height: 最大高度

        Returns:
            新的宽度和高度元组
        """
        if not max_width and not max_height:
            return original_width, original_height

        aspect_ratio = original_width / original_height

        # 如果两者都设置了
        if max_width and max_height:
            # 以宽度为基准计算高度
            width_based_height = max_width / aspect_ratio
            if width_based_height <= max_height:
                # 宽度受限
                new_width = max_width
                new_height = int(width_based_height)
            else:
                # 高度受限
                new_height = max_height
                new_width = int(new_height * aspect_ratio)
        elif max_width:
            # 只设置了最大宽度
            if original_width > max_width:
                new_width = max_width
                new_height = int(max_width / aspect_ratio)
            else:
                new_width = original_width
                new_height = original_height
        else:
            # 只设置了最大高度
            if original_height > max_height:
                new_height = max_height
                new_width = int(max_height * aspect_ratio)
            else:
                new_width = original_width
                new_height = original_height

        return new_width, new_height

    @staticmethod
    def compress_image(
        input_path: str,
        output_path: str,
        quality: str = 'medium',
        target_quality: Optional[int] = None,
        target_format: str = 'same',
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        压缩图片

        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            quality: 质量预设 (low/medium/high/custom)
            target_quality: 目标质量 (1-100)
            target_format: 目标格式 (same/jpeg/png/webp)
            max_width: 最大宽度
            max_height: 最大高度

        Returns:
            压缩结果信息
        """
        try:
            # 获取原始图片信息
            original_info = ImageCompressionService.get_image_info(input_path)

            # 打开图片
            with Image.open(input_path) as img:
                # 转换 RGBA 图片为 RGB (如果目标格式是 JPEG)
                output_format = target_format if target_format != 'same' else original_info['format'].lower()
                
                if output_format == 'jpeg' and img.mode in ('RGBA', 'LA', 'P'):
                    # 创建白色背景
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                elif img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')

                # 计算新尺寸
                new_width, new_height = ImageCompressionService.calculate_new_dimensions(
                    original_info['width'],
                    original_info['height'],
                    max_width,
                    max_height
                )

                # 如果需要缩放
                if new_width != original_info['width'] or new_height != original_info['height']:
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # 确定压缩质量
                if quality != 'custom' and quality in ImageCompressionService.QUALITY_PRESETS:
                    preset = ImageCompressionService.QUALITY_PRESETS[quality]
                    compression_quality = target_quality or preset['quality']
                    optimize = preset['optimize']
                else:
                    compression_quality = target_quality or 80
                    optimize = True

                # 确定输出格式
                save_format = ImageCompressionService.FORMAT_MAPPING.get(
                    output_format, 
                    original_info['format']
                )

                # 保存压缩后的图片
                save_kwargs = {
                    'format': save_format,
                    'optimize': optimize,
                }

                # 只有 JPEG 和 WebP 支持 quality 参数
                if save_format in ('JPEG', 'WEBP'):
                    save_kwargs['quality'] = compression_quality

                # PNG 特殊处理
                if save_format == 'PNG':
                    save_kwargs['compress_level'] = 9  # 最高压缩级别

                img.save(output_path, **save_kwargs)

            # 获取压缩后的图片信息
            compressed_info = ImageCompressionService.get_image_info(output_path)

            # 计算压缩比
            compression_ratio = compressed_info['size'] / original_info['size'] if original_info['size'] > 0 else 0

            result = {
                'success': True,
                'original_info': original_info,
                'compressed_info': compressed_info,
                'compression_ratio': compression_ratio,
                'compression_percentage': round((1 - compression_ratio) * 100, 2),
            }

            return result

        except Exception as e:
            raise Exception(f"图片压缩失败: {str(e)}")

    @staticmethod
    def process_compression_task(task):
        """
        处理图片压缩任务

        Args:
            task: ImageCompressionTask 实例
        """
        from apps.image.models import ImageCompressionTask

        try:
            # 更新任务状态为处理中
            task.status = 'processing'
            task.progress = 0
            task.save()

            # 获取原始图片路径
            input_path = task.original_image.path

            # 生成输出文件路径
            original_name = Path(task.original_image.name).stem
            
            # 确定输出格式
            if task.target_format == 'same':
                original_ext = Path(task.original_image.name).suffix
                output_ext = original_ext
            else:
                output_ext = f'.{task.target_format}'
            
            output_filename = f"{original_name}_compressed{output_ext}"

            # 获取media根目录
            from django.conf import settings
            media_root = Path(settings.MEDIA_ROOT)

            # 创建压缩图片目录：media/images/compressed/YYYY/MM/DD/
            output_dir = media_root / 'images' / 'compressed' / timezone.now().strftime('%Y/%m/%d')
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / output_filename

            # 获取原始图片信息
            original_info = ImageCompressionService.get_image_info(input_path)
            task.original_size = original_info['size']
            task.original_width = original_info['width']
            task.original_height = original_info['height']
            task.original_format = original_info['format']
            task.progress = 10
            task.save()

            # 执行压缩
            result = ImageCompressionService.compress_image(
                input_path=input_path,
                output_path=str(output_path),
                quality=task.quality,
                target_quality=task.target_quality,
                target_format=task.target_format,
                max_width=task.max_width,
                max_height=task.max_height,
            )

            task.progress = 90
            task.save()

            # 保存压缩后的图片
            with open(output_path, 'rb') as f:
                task.compressed_image.save(
                    output_filename,
                    File(f),
                    save=False
                )

            # 更新任务信息
            task.compressed_size = result['compressed_info']['size']
            task.compressed_width = result['compressed_info']['width']
            task.compressed_height = result['compressed_info']['height']
            task.compressed_format = result['compressed_info']['format']
            task.compression_ratio = result['compression_ratio']
            task.status = 'completed'
            task.progress = 100
            task.completed_at = timezone.now()
            task.save()

            # 删除临时压缩文件
            try:
                if output_path.exists():
                    output_path.unlink()
            except Exception as e:
                print(f"删除临时文件失败: {str(e)}")

            return result

        except Exception as e:
            task.status = 'failed'
            task.error_message = str(e)
            task.save()
            
            # 如果压缩失败，也尝试清理临时文件
            try:
                if 'output_path' in locals() and output_path.exists():
                    output_path.unlink()
            except Exception as cleanup_error:
                print(f"清理临时文件失败: {str(cleanup_error)}")
            
            raise

