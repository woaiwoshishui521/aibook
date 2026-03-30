#!/bin/bash

# 停止所有服务

# 项目根目录
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# 日志目录
LOG_DIR="$PROJECT_DIR/logs"

echo "=========================================="
echo "停止所有服务"
echo "=========================================="

# 停止Django服务器
DJANGO_PID_FILE="$LOG_DIR/django.pid"
if [ -f "$DJANGO_PID_FILE" ]; then
    DJANGO_PID=$(cat "$DJANGO_PID_FILE")
    if ps -p "$DJANGO_PID" > /dev/null 2>&1; then
        echo "停止Django服务器 (PID: $DJANGO_PID)..."
        kill "$DJANGO_PID"
        rm -f "$DJANGO_PID_FILE"
        echo "Django服务器已停止"
    else
        echo "Django服务器未运行"
        rm -f "$DJANGO_PID_FILE"
    fi
else
    echo "Django服务器未运行"
fi

# 停止Celery Worker
CELERY_PID_FILE="$LOG_DIR/celery.pid"
if [ -f "$CELERY_PID_FILE" ]; then
    CELERY_PID=$(cat "$CELERY_PID_FILE")
    if ps -p "$CELERY_PID" > /dev/null 2>&1; then
        echo "停止Celery Worker (PID: $CELERY_PID)..."
        kill "$CELERY_PID"
        rm -f "$CELERY_PID_FILE"
        echo "Celery Worker已停止"
    else
        echo "Celery Worker未运行"
        rm -f "$CELERY_PID_FILE"
    fi
else
    echo "Celery Worker未运行"
fi

# 清理可能残留的进程
echo ""
echo "清理残留进程..."
pkill -f "manage.py runserver" 2>/dev/null && echo "已清理Django残留进程"
pkill -f "celery -A config worker" 2>/dev/null && echo "已清理Celery残留进程"

echo ""
echo "=========================================="
echo "所有服务已停止"
echo "=========================================="
