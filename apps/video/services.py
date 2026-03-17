"""
视频压缩服务
使用 ffmpeg-python 进行视频压缩处理
"""
import os
import ffmpeg
from pathlib import Path
from typing import Optional, Dict, Any
from django.core.files import File
from django.utils import timezone


class VideoCompressionService:
    """视频压缩服务类"""

    # 预设质量配置
    QUALITY_PRESETS = {
        'low': {
            'resolution': '854x480',
            'bitrate': '500k',
            'fps': 24,
        },
        'medium': {
            'resolution': '1280x720',
            'bitrate': '1000k',
            'fps': 30,
        },
        'high': {
            'resolution': '1920x1080',
            'bitrate': '2000k',
            'fps': 30,
        },
    }

    @staticmethod
    def get_video_info(video_path: str) -> Dict[str, Any]:
        """
        获取视频信息

        Args:
            video_path: 视频文件路径

        Returns:
            包含视频信息的字典
        """
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)

            if video_stream is None:
                raise ValueError("无法找到视频流")

            info = {
                'duration': float(probe['format'].get('duration', 0)),
                'size': int(probe['format'].get('size', 0)),
                'bitrate': probe['format'].get('bit_rate', 'unknown'),
                'resolution': f"{video_stream['width']}x{video_stream['height']}",
                'width': video_stream['width'],
                'height': video_stream['height'],
                'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                'codec': video_stream.get('codec_name', 'unknown'),
                'has_audio': audio_stream is not None,
            }

            return info
        except Exception as e:
            raise Exception(f"获取视频信息失败: {str(e)}")

    @staticmethod
    def compress_video(
        input_path: str,
        output_path: str,
        quality: str = 'medium',
        resolution: Optional[str] = None,
        bitrate: Optional[str] = None,
        fps: Optional[int] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        压缩视频

        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            quality: 质量预设 (low/medium/high/custom)
            resolution: 目标分辨率 (例如: '1280x720')
            bitrate: 目标比特率 (例如: '1000k')
            fps: 目标帧率
            progress_callback: 进度回调函数

        Returns:
            压缩结果信息
        """
        try:
            # 获取原始视频信息
            original_info = VideoCompressionService.get_video_info(input_path)

            # 确定压缩参数
            if quality != 'custom' and quality in VideoCompressionService.QUALITY_PRESETS:
                preset = VideoCompressionService.QUALITY_PRESETS[quality]
                resolution = resolution or preset['resolution']
                bitrate = bitrate or preset['bitrate']
                fps = fps or preset['fps']

            # 解析分辨率
            if resolution:
                width, height = map(int, resolution.split('x'))
            else:
                width, height = original_info['width'], original_info['height']

            # 构建 ffmpeg 命令
            stream = ffmpeg.input(input_path)

            # 视频流处理
            video = stream.video.filter('scale', width, height)

            # 输出配置
            output_kwargs = {
                'video_bitrate': bitrate or '1000k',
                'r': fps or 30,
                'vcodec': 'libx264',
                'preset': 'medium',  # 编码速度预设
                'crf': 23,  # 恒定质量因子 (0-51, 越小质量越好)
            }

            # 检查是否有音频流
            if original_info['has_audio']:
                # 有音频流，同时处理音频和视频
                audio = stream.audio
                output_kwargs['acodec'] = 'aac'
                output_kwargs['audio_bitrate'] = '128k'

                output = ffmpeg.output(
                    video,
                    audio,
                    output_path,
                    **output_kwargs
                )
            else:
                # 没有音频流，只处理视频
                output = ffmpeg.output(
                    video,
                    output_path,
                    **output_kwargs
                )

            # 覆盖已存在的文件
            output = ffmpeg.overwrite_output(output)

            # 运行 ffmpeg
            ffmpeg.run(output, capture_stdout=True, capture_stderr=True)

            # 获取压缩后的视频信息
            compressed_info = VideoCompressionService.get_video_info(output_path)

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

        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            raise Exception(f"视频压缩失败: {error_message}")
        except Exception as e:
            raise Exception(f"视频压缩失败: {str(e)}")

    @staticmethod
    def process_compression_task(task):
        """
        处理视频压缩任务

        Args:
            task: VideoCompressionTask 实例
        """
        from apps.video.models import VideoCompressionTask

        try:
            # 更新任务状态为处理中
            task.status = 'processing'
            task.progress = 0
            task.save()

            # 获取原始视频路径
            input_path = task.original_video.path

            # 生成输出文件路径
            original_name = Path(task.original_video.name).stem
            output_filename = f"{original_name}_compressed.mp4"

            # 获取media根目录
            from django.conf import settings
            media_root = Path(settings.MEDIA_ROOT)

            # 创建压缩视频目录：media/videos/compressed/YYYY/MM/DD/
            output_dir = media_root / 'videos' / 'compressed' / timezone.now().strftime('%Y/%m/%d')
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / output_filename

            # 获取原始视频信息
            original_info = VideoCompressionService.get_video_info(input_path)
            task.original_size = original_info['size']
            task.original_duration = original_info['duration']
            task.original_resolution = original_info['resolution']
            task.original_bitrate = str(original_info['bitrate'])
            task.progress = 10
            task.save()

            # 执行压缩
            result = VideoCompressionService.compress_video(
                input_path=input_path,
                output_path=str(output_path),
                quality=task.quality,
                resolution=task.target_resolution,
                bitrate=task.target_bitrate,
                fps=task.target_fps,
            )

            task.progress = 90
            task.save()

            # 保存压缩后的视频
            with open(output_path, 'rb') as f:
                task.compressed_video.save(
                    output_filename,
                    File(f),
                    save=False
                )

            # 更新任务信息
            task.compressed_size = result['compressed_info']['size']
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
                if output_path.exists():
                    output_path.unlink()
            except Exception as cleanup_error:
                print(f"清理临时文件失败: {str(cleanup_error)}")
            
            raise



