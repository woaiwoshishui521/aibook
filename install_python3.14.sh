#!/bin/bash

# 使用 pyenv 安装 Python 3.14 版本的脚本

set -e  # 遇到错误立即退出

echo "==================================="
echo "开始安装 Python 3.14"
echo "==================================="

# 检查 pyenv 是否已安装
if ! command -v pyenv &> /dev/null; then
    echo "错误: pyenv 未安装"
    echo "请先安装 pyenv: https://github.com/pyenv/pyenv#installation"
    exit 1
fi

echo "✓ pyenv 已安装"

# 更新 pyenv 以获取最新的 Python 版本列表
echo ""
echo "正在更新 pyenv..."
cd "$(pyenv root)" && git pull

# 检查 Python 3.14 是否可用
echo ""
echo "检查可用的 Python 3.14 版本..."
AVAILABLE_VERSIONS=$(pyenv install --list | grep -E "^\s*3\.14\." | sed 's/^[[:space:]]*//')

if [ -z "$AVAILABLE_VERSIONS" ]; then
    echo "错误: 未找到 Python 3.14 版本"
    echo "请检查 pyenv 是否已更新到最新版本"
    exit 1
fi

echo "可用的 Python 3.14 版本:"
echo "$AVAILABLE_VERSIONS"

# 获取最新的 3.14 版本
LATEST_VERSION="$(echo "$AVAILABLE_VERSIONS" | tail -n 1)"
LATEST_VERSION="3.14.3"
echo ""
echo "将安装最新版本: $LATEST_VERSION"

# 安装 Python 3.14
echo ""
echo "正在安装 Python $LATEST_VERSION..."
pyenv install "$LATEST_VERSION"

# 设置为全局版本（可选）
read -p "是否将 Python $LATEST_VERSION 设置为全局默认版本? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pyenv global "$LATEST_VERSION"
    echo "✓ 已设置 Python $LATEST_VERSION 为全局版本"
fi

# 验证安装
echo ""
echo "验证安装..."
pyenv versions | grep "$LATEST_VERSION"

echo ""
echo "==================================="
echo "✓ Python $LATEST_VERSION 安装完成!"
echo "==================================="
echo ""
echo "使用方法:"
echo "  - 设置为全局版本: pyenv global $LATEST_VERSION"
echo "  - 设置为本地版本: pyenv local $LATEST_VERSION"
echo "  - 临时使用: pyenv shell $LATEST_VERSION"
echo ""
