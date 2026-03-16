# AIBook Django REST API

一个完整的 Django REST API 项目模板，包含用户认证、缓存、监控、测试等企业级功能。

## 功能特性

- **Django 4.2+** + **Django REST Framework**
- **JWT 认证** (Simple JWT)
- **Redis 缓存**
- **PostgreSQL 数据库**
- **API 文档** (Swagger/ReDoc)
- **监控告警** (Sentry, Prometheus)
- **测试框架** (Pytest)
- **Docker 部署**
- **Celery 异步任务**

## 项目结构

```
aibook/
├── apps/                   # 应用模块
│   ├── core/              # 核心模块
│   │   ├── models.py      # 基础模型
│   │   ├── pagination.py  # 分页器
│   │   ├── exceptions.py  # 异常处理
│   │   └── views.py       # 基础视图
│   └── users/             # 用户模块
│       ├── models.py      # 用户模型
│       ├── serializers.py # 序列化器
│       ├── views.py       # API视图
│       └── urls.py        # 路由
├── config/                # 项目配置
│   ├── settings/          # 环境配置
│   │   ├── base.py       # 基础配置
│   │   ├── local.py      # 开发环境
│   │   ├── production.py # 生产环境
│   │   └── test.py       # 测试环境
│   ├── urls.py           # 主路由
│   └── celery.py         # Celery配置
├── tests/                 # 测试
│   └── conftest.py       # Pytest配置
├── requirements.txt       # 依赖
├── docker-compose.yml     # Docker编排
├── Makefile              # 常用命令
└── README.md             # 项目说明
```

## 快速开始

### 1. 本地开发

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 复制环境变量
cp .env.example .env

# 数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

### 2. Docker 部署

```bash
# 开发环境
docker-compose -f docker-compose.dev.yml up -d

# 生产环境
docker-compose up -d
```

## API 端点

### 认证相关

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/register/` | 用户注册 |
| POST | `/api/v1/auth/login/` | 用户登录 |
| POST | `/api/v1/auth/logout/` | 用户登出 |
| POST | `/api/v1/auth/refresh/` | 刷新Token |
| GET | `/api/v1/auth/profile/` | 用户信息 |
| PATCH | `/api/v1/auth/profile/` | 更新信息 |
| POST | `/api/v1/auth/change-password/` | 修改密码 |

### 文档

- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI Schema: `/api/schema/`

### 监控

- Prometheus Metrics: `/metrics/`

## 测试

```bash
# 运行所有测试
pytest

# 带覆盖率
pytest --cov=apps --cov-report=html

# 只运行单元测试
pytest -m unit
```

## 常用命令

```bash
# 使用 Makefile
make help          # 查看所有命令
make install       # 安装依赖
make migrate       # 数据库迁移
make run           # 启动服务
make test          # 运行测试
make coverage      # 测试覆盖率
make docker-up     # 启动Docker
make docker-down   # 停止Docker
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEBUG` | 调试模式 | `True` |
| `SECRET_KEY` | Django密钥 | 必填 |
| `DB_NAME` | 数据库名 | `aibook` |
| `DB_USER` | 数据库用户 | `postgres` |
| `DB_PASSWORD` | 数据库密码 | 必填 |
| `REDIS_URL` | Redis连接 | `redis://localhost:6379/0` |
| `SENTRY_DSN` | Sentry DSN | 可选 |

## 开发规范

1. **代码风格**: 使用 Black 格式化
2. **API 版本**: 使用 `/api/v1/` 前缀
3. **权限控制**: 默认需要认证，公开接口需显式设置
4. **错误处理**: 统一异常格式
5. **测试覆盖**: 核心功能需有单元测试

## 许可证

MIT License
