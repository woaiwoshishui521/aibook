# Django Settings 配置说明

## 目录结构


config/settings/
├── __init__.py      # 配置入口，根据环境变量自动加载对应配置
├── base.py          # 基础配置（所有环境共用）
├── local.py         # 本地开发环境配置
├── production.py    # 生产环境配置
└── test.py          # 测试环境配置


## 配置加载逻辑

Django 通过 `DJANGO_SETTINGS_MODULE=config.settings` 加载配置。

`config/settings/__init__.py` 会根据环境变量 `DJANGO_ENV` 自动选择加载哪个配置文件：

- `DJANGO_ENV=production` → 加载 `production.py`
- `DJANGO_ENV=test` → 加载 `test.py`
- `DJANGO_ENV=local` 或未设置 → 加载 `local.py`（默认）

## 环境变量配置

项目根目录的 `.env` 文件用于配置环境变量：


# 环境选择（可选，默认为 local）
DJANGO_ENV=local

# 基础配置
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库配置（生产环境）
DB_NAME=aibook
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# 其他配置...


## 各配置文件说明

### base.py - 基础配置
包含所有环境共用的配置：
- Django 应用列表
- 中间件配置
- 模板配置
- 静态文件配置
- REST Framework 配置
- 等等

### local.py - 本地开发环境
- `DEBUG = True`
- 使用 SQLite 数据库
- 使用本地内存缓存
- 启用 Django Debug Toolbar
- 详细的日志输出

### production.py - 生产环境
- `DEBUG = False`
- 使用 PostgreSQL 数据库
- 使用 Redis 缓存
- 启用安全设置（SSL、HSTS 等）
- 集成 Sentry 错误监控
- 生产级日志配置

### test.py - 测试环境
- 用于运行单元测试和集成测试
- 使用内存数据库（更快）
- 禁用不必要的中间件

## 使用方法

### 本地开发

# 默认使用 local.py
python manage.py runserver

# 或显式指定
export DJANGO_ENV=local
python manage.py runserver


### 生产环境

export DJANGO_ENV=production
python manage.py runserver
# 或使用 gunicorn
gunicorn config.wsgi:application


### 运行测试

export DJANGO_ENV=test
python manage.py test


## 注意事项

1. **不要修改 `__init__.py` 的导入逻辑**，除非你清楚自己在做什么
2. **敏感信息不要硬编码**，使用 `.env` 文件配置
3. **`.env` 文件不要提交到版本控制**，已添加到 `.gitignore`
4. **生产环境必须设置强密码的 `SECRET_KEY`**
5. **生产环境必须正确配置 `ALLOWED_HOSTS`**

## 扩展配置

如果需要添加新的环境配置（如 staging），可以：

1. 创建 `config/settings/staging.py`
2. 在 `__init__.py` 中添加对应的条件分支：


elif ENV == 'staging':
    from .staging import *


## 故障排查

### 问题：配置没有生效
- 检查 `DJANGO_ENV` 环境变量是否正确设置
- 清除 Python 缓存：`find . -name "*.pyc" -delete && find . -name "__pycache__" -delete`
- 检查 `.env` 文件是否在项目根目录

### 问题：导入错误
- 确保 `DJANGO_SETTINGS_MODULE=config.settings`
- 确保没有 `config/settings.py` 文件与 `config/settings/` 目录冲突

### 问题：环境变量读取失败
- 检查 `.env` 文件格式是否正确（`KEY=VALUE`，不要有空格）
- 确保安装了 `django-environ` 包
