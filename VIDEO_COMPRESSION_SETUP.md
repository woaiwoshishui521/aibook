# 视频压缩功能 - 快速开始指南

## 已完成的功能

✅ 完整的视频压缩Django应用
✅ 使用ffmpeg-python进行视频处理
✅ RESTful API接口
✅ 美观的Web操作界面
✅ 实时进度显示
✅ 任务管理和统计
✅ 文件上传和下载
✅ 测试用例

## 安装步骤

### 1. 安装系统依赖 - FFmpeg

**macOS:**

brew install ffmpeg


**Ubuntu/Debian:**

sudo apt update
sudo apt install ffmpeg


**验证安装:**

ffmpeg -version


### 2. 安装Python依赖


pip install -r requirements.txt


主要新增的依赖：
- `ffmpeg-python>=0.2.0` - Python的FFmpeg封装库
- `Pillow>=10.0.0` - 图像处理库

### 3. 运行数据库迁移


# 创建迁移文件
python manage.py makemigrations video

# 执行迁移
python manage.py migrate


### 4. 创建媒体文件目录


mkdir -p media/videos/original
mkdir -p media/videos/compressed


### 5. 启动开发服务器


python manage.py runserver


## 访问应用

### Web界面
打开浏览器访问：`http://localhost:8000/video/`

功能包括：
- 📤 拖拽或点击上传视频
- ⚙️ 选择压缩质量（低/中/高/自定义）
- 📊 实时查看压缩进度
- 📥 下载压缩后的视频
- 📈 查看统计信息

### API接口

#### 1. 创建压缩任务

curl -X POST http://localhost:8000/video/api/tasks/ \
  -F "title=测试视频压缩" \
  -F "original_video=@/path/to/video.mp4" \
  -F "quality=medium"


#### 2. 获取任务列表

curl http://localhost:8000/video/api/tasks/


#### 3. 获取任务详情

curl http://localhost:8000/video/api/tasks/1/


#### 4. 下载压缩后的视频

curl -O http://localhost:8000/video/api/tasks/1/download/


#### 5. 重试失败的任务

curl -X POST http://localhost:8000/video/api/tasks/1/retry/


#### 6. 获取统计信息

curl http://localhost:8000/video/api/tasks/statistics/


## 压缩质量说明

### 预设质量

| 质量 | 分辨率 | 比特率 | 帧率 | 文件大小 |
|------|--------|--------|------|----------|
| 低质量 (low) | 854x480 | 500k | 24fps | 最小 |
| 中等质量 (medium) | 1280x720 | 1000k | 30fps | 中等 (推荐) |
| 高质量 (high) | 1920x1080 | 2000k | 30fps | 较大 |

### 自定义参数

选择 `quality=custom` 时，可以自定义：
- `target_resolution`: 例如 "1280x720"
- `target_bitrate`: 例如 "1000k"
- `target_fps`: 例如 30

示例：

curl -X POST http://localhost:8000/video/api/tasks/ \
  -F "title=自定义压缩" \
  -F "original_video=@video.mp4" \
  -F "quality=custom" \
  -F "target_resolution=1280x720" \
  -F "target_bitrate=800k" \
  -F "target_fps=25"


## 支持的视频格式

- MP4
- AVI
- MOV
- MKV
- FLV
- WMV

## 文件大小限制

当前限制：**500MB**

如需修改，编辑 `apps/video/serializers.py` 中的 `validate_original_video` 方法。

## 目录结构


apps/video/
├── __init__.py
├── admin.py                    # Django管理后台
├── apps.py                     # 应用配置
├── models.py                   # VideoCompressionTask模型
├── serializers.py              # API序列化器
├── services.py                 # 视频压缩核心服务
├── tests.py                    # 测试用例
├── urls.py                     # URL路由
├── views.py                    # 视图和API
├── README.md                   # 详细文档
└── templates/
    └── video/
        └── compression.html    # Web界面


## 运行测试


python manage.py test apps.video


## Django Admin管理

1. 创建超级用户：

python manage.py createsuperuser


2. 访问管理后台：

http://localhost:8000/admin/


3. 在"视频压缩任务"中可以查看和管理所有压缩任务

## 常见问题

### Q: 提示"No module named 'environ'"
A: 运行 `pip install django-environ`

### Q: 提示"No module named 'ffmpeg'"
A: 运行 `pip install ffmpeg-python`

### Q: FFmpeg not found
A: 确保已安装FFmpeg系统工具，运行 `ffmpeg -version` 验证

### Q: 压缩任务一直处于"处理中"状态
A: 检查服务器日志，确保FFmpeg正确安装且视频文件格式正确

### Q: 如何修改压缩参数？
A: 编辑 `apps/video/services.py` 中的 `QUALITY_PRESETS` 和 `compress_video` 方法

## 性能建议

### 生产环境优化

1. **使用Celery处理任务**
   - 当前使用线程处理，生产环境建议使用Celery
   - 避免长时间任务阻塞Web服务器

2. **配置Redis缓存**
   - 缓存任务状态
   - 缓存统计信息

3. **使用云存储**
   - 将视频文件存储到AWS S3或阿里云OSS
   - 减轻服务器存储压力

4. **限制并发任务数**
   - 避免同时处理过多视频导致服务器资源耗尽

5. **定期清理旧文件**
   - 设置文件保留策略
   - 自动删除超过一定时间的文件

## 下一步改进

可以考虑添加以下功能：

- [ ] 集成Celery异步任务队列
- [ ] 视频预览功能
- [ ] 批量上传和压缩
- [ ] 视频格式转换
- [ ] 视频剪辑功能
- [ ] 添加水印
- [ ] 音频提取
- [ ] 云存储集成（S3/OSS）
- [ ] 进度WebSocket实时推送
- [ ] 用户配额管理

## 技术支持

如有问题，请查看：
1. `apps/video/README.md` - 详细文档
2. Django日志输出
3. 浏览器控制台错误信息

## 项目文件清单

已创建的文件：
- ✅ `apps/video/__init__.py`
- ✅ `apps/video/apps.py`
- ✅ `apps/video/models.py`
- ✅ `apps/video/admin.py`
- ✅ `apps/video/serializers.py`
- ✅ `apps/video/services.py`
- ✅ `apps/video/views.py`
- ✅ `apps/video/urls.py`
- ✅ `apps/video/tests.py`
- ✅ `apps/video/templates/video/compression.html`
- ✅ `apps/video/README.md`

已修改的文件：
- ✅ `requirements.txt` - 添加ffmpeg-python和Pillow
- ✅ `config/settings/base.py` - 添加apps.video到INSTALLED_APPS
- ✅ `config/urls.py` - 添加video路由

## 开始使用

现在你可以：

1. 安装依赖：`pip install -r requirements.txt`
2. 安装FFmpeg：`brew install ffmpeg` (macOS)
3. 运行迁移：`python manage.py makemigrations && python manage.py migrate`
4. 启动服务：`python manage.py runserver`
5. 访问：`http://localhost:8000/video/`

祝你使用愉快！🎬
