# 修复：文件路径问题

## ✅ 已修复的问题

**问题描述**：压缩后的视频文件被错误地保存在 `media/videos/original/2026/03/17/compressed/` 目录下，而不是正确的 `media/videos/compressed/` 目录下。

**原因分析**：
原代码使用了相对路径计算：

output_dir = Path(task.original_video.path).parent.parent / 'compressed' / ...


这会从原始视频路径 `media/videos/original/2026/03/17/video.mp4` 向上两级，到达 `media/videos/original/2026/`，然后创建 `compressed` 目录，导致结构混乱。

**修复方案**：
使用绝对路径从 `MEDIA_ROOT` 开始构建：

from django.conf import settings
media_root = Path(settings.MEDIA_ROOT)
output_dir = media_root / 'videos' / 'compressed' / timezone.now().strftime('%Y/%m/%d')


## 📁 正确的目录结构

修复后，文件结构应该是：


media/
├── videos/
│   ├── original/           # 原始视频
│   │   └── 2026/
│   │       └── 03/
│   │           └── 17/
│   │               ├── input.mp4
│   │               └── input_tkzluCU.mp4
│   └── compressed/         # 压缩后的视频
│       └── 2026/
│           └── 03/
│               └── 17/
│                   ├── input_compressed.mp4
│                   └── input_tkzluCU_compressed.mp4


## 🧹 清理操作

已删除错误位置的文件：

rm -rf media/videos/original/2026/03/17/compressed/


## 🔄 下一步操作

1. **重启Django服务器**：
   
   # 按 Ctrl+C 停止
   python manage.py runserver
   

2. **重新测试压缩功能**：
   - 上传新的视频
   - 开始压缩
   - 检查文件是否正确保存在 `media/videos/compressed/` 目录下

3. **可选：清理数据库中的旧任务**：
   
   python manage.py shell
   
   
   from apps.video.models import VideoCompressionTask
   # 删除所有旧任务
   VideoCompressionTask.objects.all().delete()
   

## ✅ 修复完成

现在压缩后的视频将正确保存在 `media/videos/compressed/YYYY/MM/DD/` 目录下。

## 📝 相关文件

修改的文件：
- `apps/video/services.py` (第195-206行)

主要改动：
- 使用 `settings.MEDIA_ROOT` 获取媒体根目录
- 使用绝对路径构建输出目录
- 确保目录结构清晰且符合预期
