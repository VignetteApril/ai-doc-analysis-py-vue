@echo off
REM AI 公文校对系统 - 本地开发启动脚本 (Windows)
REM 用于同时启动前后端服务

echo 🚀 启动 AI 公文校对系统开发环境
echo ================================

REM 检查是否在项目根目录
if not exist "docker-compose.yml" (
    echo ❌ 错误: 请在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 启动后端服务 (Docker Compose)
echo 🔧 启动后端服务...
docker-compose up -d

if %errorlevel% neq 0 (
    echo ❌ 后端服务启动失败
    pause
    exit /b 1
)

echo ✅ 后端服务已启动 (http://localhost:8000)

REM 启动前端服务
echo 🔧 启动前端服务...
cd frontend
if %errorlevel% neq 0 (
    echo ❌ 前端目录不存在
    cd ..
    pause
    exit /b 1
)

REM 安装依赖（如果需要）
if not exist "node_modules" (
    echo 📦 安装前端依赖...
    npm install
)

REM 启动开发服务器
echo 🚀 前端开发服务器启动中...
start "Frontend Dev Server" cmd /c "npm run dev"

cd ..

echo ✅ 前端服务已启动 (http://localhost:5173 或其他可用端口)
echo.
echo 📋 服务地址:
echo    后端 API: http://localhost:8000
echo    前端界面: http://localhost:5173
echo.
echo 💡 使用说明:
echo    - 关闭前端命令窗口即可停止前端服务
echo    - 如需停止后端服务，运行: docker-compose down
echo.

pause