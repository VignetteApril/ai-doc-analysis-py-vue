from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# 引入 v1 版本的路由总汇
from app.api.v1.api import api_router
# 引入所有模型，确保 create_all 时能扫描到新表
from app.db.database import Base, engine
from app.models import user, document, vocabulary  # noqa: F401

# 自动创建缺失的表（幂等操作，不影响已有数据）
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI 公文校对系统 API",
    description="后端 API 服务",
    version="1.0.0"
)

# --- 1. 跨域配置 (CORS) ---
# 考虑到你可能在不同环境下调试，建议保留并稍微扩大范围
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://0.0.0.0:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. 路由挂载 ---
# 所有的 v1 接口都通过 api_router 统一挂载
# 这样做的好处是：未来如果你有 v2 版本，直接再加一行即可，main.py 结构极简
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["系统自检"])
async def root():
    """根路径测试"""
    return {
        "status": "online",
        "message": "AI 公文校对系统后端已启动",
        "docs_url": "/docs"
    }

# --- 3. 运行配置 ---
if __name__ == "__main__":
    import uvicorn
    # 提醒：在 Docker 环境下，通常由 docker-compose 的 command 启动 uvicorn
    # 这里的代码主要用于你在容器内手动执行 python main.py 调试
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)