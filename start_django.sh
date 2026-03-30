#!/bin/bash

# Django开发服务器启动脚本

# 项目根目录
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# 日志目录
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

# PID文件
PID_FILE="$LOG_DIR/django.pid"

# 检查是否已经在运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Django服务器已经在运行 (PID: $PID)"
        exit 1
    else
        rm -f "$PID_FILE"
    fi
fi

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "激活虚拟环境..."
    source .venv/bin/activate
fi

# 运行数据库迁移
echo "检查数据库迁移..."
python manage.py migrate --noinput

# 收集静态文件（生产环境）
# python manage.py collectstatic --noinput

# 启动Django服务器
echo "启动Django开发服务器..."
nohup python manage.py runserver 0.0.0.0:8000 > "$LOG_DIR/django.log" 2>&1 &
echo $! > "$PID_FILE"

echo "Django服务器已启动 (PID: $(cat $PID_FILE))"
echo "日志文件: $LOG_DIR/django.log"
echo "访问地址: http://localhost:8000"
