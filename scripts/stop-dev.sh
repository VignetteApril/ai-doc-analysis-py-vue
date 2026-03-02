#!/bin/bash

# AI 公文校对系统 - 停止开发环境脚本
# 用于停止所有开发服务

echo "🛑 停止 AI 公文校对系统开发环境"
echo "==============================="

# 检查是否在项目根目录
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 停止后端服务
echo "🔧 停止后端服务..."
docker-compose down

echo "✅ 开发环境已完全停止"