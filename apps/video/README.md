# 视频压缩功能使用指南

## 功能概述

这是一个基于Django的视频压缩功能，使用FFmpeg进行高效的视频压缩处理。支持多种视频格式，提供三种预设质量级别和自定义压缩参数。

## 主要特性

- 🎬 支持多种视频格式：MP4, AVI, MOV, MKV, FLV, WMV
- 📊 三种预设质量级别：低(480p)、中(720p)、高(1080p)
- 🎨 自定义压缩参数：分辨率、比特率、帧率
- 📈 实时进度显示
- 📥 压缩后视频下载
- 📊 统计信息展示
- 🔄 失败任务重试
- 🎯 拖拽上传支持

## 技术栈

- **后端框架**: Django 4.2+ / Django REST Framework
- **视频处理**: FFmpeg / ffmpeg-python
- **前端**: 原生HTML/CSS/JavaScript
- **数据库**: PostgreSQL (可配置)

## 安装步骤

### 1. 安装系统依赖

首先需要安装FFmpeg：

**macOS:**

brew install ffmpeg


**Ubuntu/Debian:**

sudo apt update
sudo apt install ffmpeg


**Windows:**
从 [FFmpeg官网](https://ffmpeg.org/download.html) 下载并安装

### 2. 安装Python依赖


pip install -r requirements.txt


### 3. 运行数据库迁移


python manage.py makemigrations video
python manage.py migrate


### 4. 创建媒体文件目录


mkdir -p media/videos/original
mkdir -p media/videos/compressed


### 5. 启动开发服务器


python manage.py runserver


## 使用方法

### 通过Web界面使用

1. 访问 `http://localhost:8000/video/`
2. 点击或拖拽上传视频文件
3. 填写任务名称
4. 选择压缩质量（或自定义参数）
5. 点击"开始压缩"
6. 等待处理完成后下载压缩后的视频

### 通过API使用

#### 创建压缩任务


curl -X POST http://localhost:8000/video/api/tasks/ \
  -F "title=我的视频压缩" \
  -F "original_video=@/path/to/video.mp4" \
  -F "quality=medium"


#### 获取任务列表


curl http://localhost:8000/video/api/tasks/


#### 获取任务详情


curl http://localhost:8000/video/api/tasks/{task_id}/


#### 下载压缩后的视频


curl -O http://localhost:8000/video/api/tasks/{task_id}/download/


#### 重试失败的任务


curl -X POST http://localhost:8000/video/api/tasks/{task_id}/retry/


#### 获取统计信息


curl http://localhost:8000/video/api/tasks/statistics/


## 压缩参数说明

### 预设质量级别

| 质量 | 分辨率 | 比特率 | 帧率 | 适用场景 |
|------|--------|--------|------|----------|
| 低质量 | 854x480 | 500k | 24fps | 社交媒体分享 |
| 中等质量 | 1280x720 | 1000k | 30fps | 一般用途(推荐) |
| 高质量 | 1920x1080 | 2000k | 30fps | 保留更多细节 |

### 自定义参数

选择"自定义"质量后，可以设置：

- **分辨率**: 格式为 `宽x高`，例如 `1280x720`
- **比特率**: 格式为数字+单位，例如 `1000k` 或 `2M`
- **帧率**: 整数，例如 `30` 或 `60`

## 文件结构


apps/video/
├── __init__.py
├── admin.py              # Django管理后台配置
├── apps.py               # 应用配置
├── models.py             # 数据模型
├── serializers.py        # DRF序列化器
├── services.py           # 视频压缩核心服务
├── tests.py              # 测试用例
├── urls.py               # URL路由
├── views.py              # 视图函数
└── templates/
    └── video/
        └── compression.html  # 前端页面


## API响应示例

### 任务对象


{
  "id": 1,
  "title": "我的视频压缩",
  "original_video": "/media/videos/original/2024/03/17/video.mp4",
  "compressed_video": "/media/videos/compressed/2024/03/17/video_compressed.mp4",
  "quality": "medium",
  "quality_display": "中等质量 (720p)",
  "status": "completed",
  "status_display": "已完成",
  "progress": 100,
  "original_size_mb": 50.5,
  "compressed_size_mb": 15.2,
  "compression_percentage": 69.9,
  "original_resolution": "1920x1080",
  "original_duration": 120.5,
  "created_at": "2024-03-17T10:00:00Z",
  "completed_at": "2024-03-17T10:02:30Z"
}


### 统计信息


{
  "total": 10,
  "pending": 1,
  "processing": 2,
  "completed": 6,
  "failed": 1,
  "total_saved_mb": 250.5
}


## 性能优化建议

1. **使用Celery处理长时间任务**: 当前实现使用线程处理，生产环境建议使用Celery
2. **配置Redis缓存**: 缓存任务状态和统计信息
3. **使用云存储**: 将视频文件存储到S3或OSS
4. **限制并发任务数**: 避免服务器资源耗尽
5. **定期清理旧文件**: 设置文件保留策略

## 常见问题

### Q: 压缩速度很慢怎么办？
A: 可以调整FFmpeg的preset参数，从'medium'改为'faster'或'veryfast'，但会略微降低压缩效率。

### Q: 支持的最大文件大小是多少？
A: 当前限制为500MB，可以在serializers.py中修改。

### Q: 如何批量压缩视频？
A: 可以通过API循环创建多个任务，或扩展功能支持批量上传。

### Q: 压缩失败怎么办？
A: 检查error_message字段，确保FFmpeg正确安装，视频文件格式正确。

## 后续改进计划

- [ ] 集成Celery进行异步任务处理
- [ ] 添加视频预览功能
- [ ] 支持批量上传和压缩
- [ ] 添加更多视频格式转换选项
- [ ] 实现视频剪辑功能
- [ ] 添加水印功能
- [ ] 支持音频提取
- [ ] 云存储集成

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交Issue或Pull Request。
