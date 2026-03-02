# AGENTS.md

目标：让 agent 少猜、少绕路、少污染上下文。

## 1) 启动与测试命令

### 启动（推荐）
- 后端（Docker）：
  - `docker-compose up -d`
  - 后端地址：`http://localhost:8000`
- 前端（本地）：
  - `cd frontend`
  - `npm install`
  - `npm run dev`
  - 前端地址：`http://localhost:5173`

### 一键脚本
- Windows 本地启动：`scripts/start-dev.bat`
- Linux/macOS 本地启动：`bash scripts/start-dev.sh`
- 停止：`scripts/stop-dev.bat` / `bash scripts/stop-dev.sh`

### 测试
- 后端本地测试：
  - `cd backend`
  - `python -m pytest tests/ -v`
- 后端 Docker 测试：
  - `bash scripts/test-backend-docker.sh`
  - 或 `scripts/test-backend-docker.bat`

## 2) 日志 / DB / 部署 CLI（含 env 加载示例）

### 日志
- 查看后端日志：`docker-compose logs -f backend`
- 查看数据库日志：`docker-compose logs -f db`

### DB（PostgreSQL）
- 进入数据库容器：`docker-compose exec db psql -U postgres -d ai_doc_db`
- 常用查询：
  - `\dt`
  - `SELECT id, name, status FROM documents ORDER BY id DESC LIMIT 20;`

### 部署/运行相关
- 启动全部服务：`docker-compose up -d`
- 重建后端镜像并启动：`docker-compose up -d --build backend`
- 停止并清理容器网络：`docker-compose down`

### env 加载示例
- Linux/macOS（当前 shell 生效）：
  - `set -a; source .env; set +a`
- Windows PowerShell（当前会话生效）：
  - `Get-Content .env | ForEach-Object { if ($_ -match '^(\w+)=(.*)$') { Set-Item -Path Env:$($matches[1]) -Value $matches[2] } }`

## 3) 代码风格偏好
- 改动要小：优先最小可行修复，避免无关重构。
- 先验证：修复后至少做语法检查/构建；能补测试就补。
- 关键逻辑要注释：解释“为什么这样做”，不是解释“代码做了什么”。
- 不改无关文件：尤其不要顺手改编码、文案、格式化全文件。
- 保持兼容：接口字段名和返回结构不随意变更。

## 4) 常见坑 & 处理办法（持续追加）
- 坑：Word 表格在编辑器里变成横线/段落。
  - 处理：解析端必须保证输出真实 `<table>` 结构；若 Mammoth 丢表格，回退 `python-docx` 结构化解析。
- 坑：修了解析器但页面仍显示旧坏内容。
  - 处理：`documents.content_html` 有缓存；需重解析或清缓存后再看。
- 坑：Vue `scoped` 样式对编辑器内容不生效。
  - 处理：对 ProseMirror/Tiptap 内容使用 `:deep(...)`。
- 坑：中文乱码导致 Python/前端语法损坏。
  - 处理：统一 UTF-8（无 BOM），避免用会改编码的批量替换脚本。
