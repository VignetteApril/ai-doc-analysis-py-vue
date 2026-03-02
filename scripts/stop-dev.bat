@echo off
REM AI 公文校对系统 - 停止开发环境脚本 (Windows)
REM 用于停止所有开发服务

echo 🛑 停止 AI 公文校对系统开发环境
echo ===============================

REM 检查是否在项目根目录
if not exist "docker-compose.yml" (
    echo ❌ 错误: 请在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 停止后端服务
echo 🔧 停止后端服务...
docker-compose down

echo ✅ 开发环境已完全停止
pause