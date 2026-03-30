#!/bin/bash

# 启动所有服务

# 项目根目录
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=========================================="
echo "启动所有服务"
echo "=========================================="

# 启动Django服务器
echo ""
echo "1. 启动Django服务器..."
bash "$PROJECT_DIR/start_django.sh"

# 等待Django启动
sleep 2

# 启动Celery Worker
echo ""
echo "2. 启动Celery Worker..."
bash "$PROJECT_DIR/start_celery.sh"

echo ""
echo "=========================================="
echo "所有服务已启动"
echo "=========================================="
echo "Django: http://localhost:8000"
echo "日志目录: $PROJECT_DIR/logs"
echo ""
echo "查看日志:"
echo "  Django: tail -f logs/django.log"
echo "  Celery: tail -f logs/celery.log"
echo ""
echo "停止服务: bash stop_all.sh"
