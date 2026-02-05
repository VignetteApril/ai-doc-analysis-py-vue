# 📝 AI 公文校对系统 (AI Document Analysis System)

![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Vue 3](https://img.shields.io/badge/Frontend-Vue%203-42b883?style=for-the-badge&logo=vue.js&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/CSS-Tailwind%20v4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)
![Docker](https://img.shields.io/badge/Infrastructure-Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

本系统是一款基于深度学习技术的智能化公文处理平台，专注于为公文提供精准、高效的文字校对与合规性检查服务。项目采用前后端分离架构，通过容器化技术实现快速部署与环境隔离。

---

## 🏗️ 技术架构

### 后端 (Backend)
* **核心框架**: FastAPI (Python 3.10-slim)
* **数据库**: PostgreSQL (数据持久化)
* **异步处理**: Redis (AI 任务队列预留)
* **开发环境**: Docker Compose + VS Code Dev Container

### 前端 (Frontend)
* **框架**: Vue 3 (Vite)
* **样式**: Tailwind CSS v4 (原生支持，极致性能)
* **路由**: Vue Router
* **网络**: Axios (集成 Vite Proxy 转发)



---

## 📂 项目目录

```text
ai-doc-analysis/
├── backend/               # FastAPI 容器化后端
│   ├── app/
│   │   ├── api/           # 路由定义 (v1/auth 等)
│   │   ├── models/        # SQLAlchemy 数据库模型
│   │   └── main.py        # 应用主入口
│   ├── .devcontainer/     # VS Code 开发容器配置
│   ├── Dockerfile.dev      # 开发环境镜像定义
│   └── requirements.txt    # 后端依赖清单
├── frontend/              # Vue 3 前端
│   ├── src/
│   │   ├── assets/images/ # 静态资源 (含 login-bg.png)
│   │   ├── views/         # 页面视图 (含右置登录页)
│   │   └── router/        # 路由配置
│   ├── tailwind.config.js # Tailwind 配置
│   └── package.json
└── docker-compose.yml     # 基础设施编排 (DB/Redis/Backend)
🚀 快速启动
1. 基础设施与后端
确保已安装 Docker，在根目录下执行：

Bash
docker-compose up -d
使用 VS Code 的 Dev Containers 插件选择 Reopen in Container 即可进入完美的后端开发环境。

2. 前端启动
进入 frontend 目录：

Bash
npm install
npm run dev
访问 http://localhost:5173 即可查看已适配背景图且登录框右置的界面。

📋 项目规划 (Roadmap)
作为项目管理专业人员，本项目遵循规范的生命周期管理：

[x] 第一阶段: 基于 Docker Compose 的混合开发环境搭建

[x] 第二阶段: 高保真登录页面开发 (Tailwind v4 还原设计稿)

[ ] 第三阶段: PostgreSQL 用户模型定义与 JWT 认证流程

[ ] 第四阶段: 接入 SiliconFlow API 实现公文异步校对逻辑

[ ] 第五阶段: 内网环境离线部署方案实施