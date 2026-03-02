# 开发脚本说明

本目录包含用于本地开发的便利脚本。

## 启动开发环境

### Windows 用户
```bash
# 启动前后端服务
scripts/start-dev.bat
```

### Linux/macOS 用户
```bash
# 启动前后端服务
./scripts/start-dev.sh
```

## 停止开发环境

### Windows 用户
```bash
# 停止所有服务
scripts/stop-dev.bat
```

### Linux/macOS 用户
```bash
# 停止所有服务
./scripts/stop-dev.sh
```

## 脚本功能

- **start-dev**: 同时启动后端 (Docker Compose) 和前端 (Vite dev server)
- **stop-dev**: 停止后端服务 (Docker Compose down)

## 注意事项

- 确保已安装 Docker 和 Node.js
- 脚本必须在项目根目录运行
- 前端服务会自动选择可用端口（通常是 5173）
- 后端服务运行在 http://localhost:8000