#!/bin/bash

# Celery Worker启动脚本

# 项目根目录
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# 日志目录
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

# PID文件
PID_FILE="$LOG_DIR/celery.pid"

# 检查是否已经在运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Celery Worker已经在运行 (PID: $PID)"
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

# 启动Celery Worker
echo "启动Celery Worker..."
nohup celery -A config worker --loglevel=info > "$LOG_DIR/celery.log" 2>&1 &
echo $! > "$PID_FILE"

echo "Celery Worker已启动 (PID: $(cat $PID_FILE))"
echo "日志文件: $LOG_DIR/celery.log"
