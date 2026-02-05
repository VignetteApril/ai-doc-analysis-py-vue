from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# 引入我们刚才创建的 auth 模块
from app.api.v1.auth import router as auth_router

app = FastAPI(
    title="AI 公文校对系统 API",
    description="后端 API 服务，支持文档解析与 AI 异步校对",
    version="1.0.0"
)

# --- 核心配置：跨域支持 ---
# 允许前端宿主机地址访问接口
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法 (GET, POST, PUT, DELETE 等)
    allow_headers=["*"],  # 允许所有请求头
)

# --- 路由注册 ---
# 我们给认证接口加上 /api/v1/auth 的前缀，方便管理
app.include_router(auth_router, prefix="/api/v1/auth", tags=["用户认证"])

@app.get("/")
async def root():
    """根路径测试"""
    return {"message": "AI 公文校对系统后端已启动", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    # 这里的 app.main:app 是相对于项目根目录的路径
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)