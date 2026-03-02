#!/bin/bash

# AI 公文校对系统 - 本地开发启动脚本
# 用于同时启动前后端服务

echo "🚀 启动 AI 公文校对系统开发环境"
echo "================================"

# 检查是否在项目根目录
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 启动后端服务 (Docker Compose)
echo "🔧 启动后端服务..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ 后端服务启动失败"
    exit 1
fi

echo "✅ 后端服务已启动 (http://localhost:8000)"

# 启动前端服务
echo "🔧 启动前端服务..."
cd frontend || { echo "❌ 前端目录不存在"; exit 1; }

# 安装依赖（如果需要）
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

# 启动开发服务器
echo "🚀 前端开发服务器启动中..."
npm run dev &

# 保存前端进程ID
FRONTEND_PID=$!

echo "✅ 前端服务已启动 (http://localhost:5173 或其他可用端口)"
echo ""
echo "📋 服务地址:"
echo "   后端 API: http://localhost:8000"
echo "   前端界面: http://localhost:5173"
echo ""
echo "💡 使用说明:"
echo "   - 按 Ctrl+C 停止前端服务"
echo "   - 如需停止后端服务，运行: docker-compose down"
echo ""

# 等待用户中断
trap 'echo "👋 停止前端服务..."; kill $FRONTEND_PID 2>/dev/null; wait $FRONTEND_PID 2>/dev/null; echo "✅ 前端服务已停止"; exit 0' INT TERM

wait $FRONTEND_PID