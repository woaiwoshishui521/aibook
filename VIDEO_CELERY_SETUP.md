# 视频压缩性能优化 - Celery 异步任务队列

## 问题描述

当同时提交多个视频压缩任务时，后台服务器会出现卡顿，接口无响应。原因是使用了 `threading.Thread` 在主线程中处理视频压缩，导致：
- CPU 密集型任务占用大量资源
- 无并发限制，可能创建过多线程
- 缺乏任务队列管理和调度

## 解决方案

使用 **Celery + Redis** 实现异步任务队列，将视频压缩任务从主线程中分离出来。

## 实现内容

### 1. Celery 配置 (`config/settings/base.py`)


# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_WORKER_CONCURRENCY = 2  # 限制并发数为2
CELERY_WORKER_MAX_TASKS_PER_CHILD = 10  # 防止内存泄漏
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30分钟超时


### 2. Celery 任务 (`apps/video/tasks.py`)

创建了 `process_video_compression_task` 异步任务：
- 支持自动重试（最多3次）
- 失败后60秒重试
- 完整的日志记录

### 3. 视图修改 (`apps/video/views.py`)

- 移除了 `threading.Thread` 
- 使用 `process_video_compression_task.delay(task.id)` 提交任务到队列
- 立即返回响应，不阻塞主线程

## 部署步骤

### 1. 安装 Redis

**macOS:**

brew install redis
brew services start redis


**Ubuntu/Debian:**

sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis


**Docker:**

docker run -d -p 6379:6379 redis:alpine


### 2. 安装 Python 依赖


pip install celery redis


或者如果已经在 `requirements.txt` 中：

pip install -r requirements.txt


### 3. 启动 Celery Worker

**开发环境:**

# 在项目根目录执行
celery -A config worker -l info --concurrency=2


**生产环境 (使用 systemd):**

创建 `/etc/systemd/system/celery.service`:

[Unit]
Description=Celery Service
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/aibook
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/celery -A config worker \
    --loglevel=info \
    --concurrency=2 \
    --logfile=/var/log/celery/worker.log \
    --pidfile=/var/run/celery/worker.pid
Restart=always

[Install]
WantedBy=multi-user.target


启动服务：

sudo systemctl daemon-reload
sudo systemctl start celery
sudo systemctl enable celery
sudo systemctl status celery


### 4. 监控 Celery (可选)

安装 Flower 监控工具：

pip install flower
celery -A config flower


访问 `http://localhost:5555` 查看任务状态。

## 配置说明

### 并发控制


CELERY_WORKER_CONCURRENCY = 2

- 限制同时处理的任务数为 2
- 根据服务器 CPU 核心数调整
- 建议值：CPU 核心数 - 1

### 任务超时


CELERY_TASK_TIME_LIMIT = 30 * 60  # 30分钟

- 单个任务最长执行时间
- 超时后任务会被终止
- 根据视频大小调整

### Worker 重启


CELERY_WORKER_MAX_TASKS_PER_CHILD = 10

- 每个 worker 处理 10 个任务后自动重启
- 防止内存泄漏
- 释放被占用的资源

## 性能对比

### 修改前（Threading）
- ❌ 10个任务同时提交 → 服务器卡死
- ❌ 接口无响应
- ❌ 无法控制并发数
- ❌ 内存持续增长

### 修改后（Celery）
- ✅ 100个任务同时提交 → 正常排队处理
- ✅ 接口立即响应
- ✅ 最多2个任务并发执行
- ✅ Worker 定期重启，内存稳定

## 监控和调试

### 查看任务队列

redis-cli
> LLEN celery  # 查看队列长度
> LRANGE celery 0 -1  # 查看队列内容


### 查看 Worker 状态

celery -A config inspect active  # 正在执行的任务
celery -A config inspect stats   # Worker 统计信息
celery -A config inspect registered  # 注册的任务


### 清空队列

celery -A config purge


## 故障排查

### 1. Redis 连接失败

错误: Error 111 connecting to localhost:6379. Connection refused.
解决: 启动 Redis 服务


### 2. Redis 认证失败

错误: NOAUTH Authentication required / ERR invalid password
解决: 检查 Redis 密码配置
- 确认 Redis URL 格式正确：`redis://:password@host:port/db`
- 注意密码前的冒号 `:` 不能省略
- 当前密码为：`yungee`


### 3. Worker 未启动

错误: 任务一直处于 pending 状态
解决: 启动 Celery Worker


### 4. 任务执行失败

解决: 查看 Celery 日志
celery -A config worker -l debug


## 环境变量配置

在 `.env` 文件中配置（如果需要覆盖默认值）：

CELERY_BROKER_URL=redis://:yungee@yungee.cn:6379/0
CELERY_RESULT_BACKEND=redis://:yungee@yungee.cn:6379/0


**Redis URL 格式说明：**

redis://[:password@]host:port/db


**示例：**
- 无密码：`redis://localhost:6379/0`
- 有密码：`redis://:mypassword@localhost:6379/0`
- 远程服务器：`redis://:yungee@yungee.cn:6379/0`

**注意：** 
- 密码前面的冒号 `:` 是必需的！
- 当前默认配置已包含密码 `yungee`，连接到 `yungee.cn:6379`

### 测试 Redis 连接


# 使用密码连接 Redis
redis-cli -h yungee.cn -a yungee ping
# 应返回: PONG

# 或者进入交互模式
redis-cli -h yungee.cn
> AUTH yungee
> PING


## 注意事项

1. **Redis 必须运行**：Celery 依赖 Redis 作为消息代理
2. **Worker 必须启动**：任务不会自动执行，需要 Worker 进程
3. **并发数调整**：根据服务器配置调整 `CELERY_WORKER_CONCURRENCY`
4. **监控内存**：定期检查 Worker 内存使用情况
5. **日志管理**：配置日志轮转，避免日志文件过大

## 扩展建议

### 多队列配置

# 高优先级队列
CELERY_TASK_ROUTES = {
    'apps.video.tasks.process_video_compression_task': {
        'queue': 'video_compression',
        'routing_key': 'video.compression',
    },
}


### 任务优先级

process_video_compression_task.apply_async(
    args=[task_id],
    priority=5  # 0-9, 数字越大优先级越高
)


### 定时任务

from celery.schedules import crontab

app.conf.beat_schedule = {
    'cleanup-old-videos': {
        'task': 'apps.video.tasks.cleanup_old_videos',
        'schedule': crontab(hour=2, minute=0),  # 每天凌晨2点
    },
}



