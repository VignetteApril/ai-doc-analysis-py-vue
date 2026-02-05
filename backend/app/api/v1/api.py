from fastapi import APIRouter
from app.api.v1.endpoints import auth

api_router = APIRouter()

# 这里就像插线板一样，把不同的接口模块插进来
api_router.include_router(auth.router, prefix="/auth", tags=["认证相关"])

# 后续你可以直接在这里加：
# api_router.include_router(docs.router, prefix="/docs", tags=["公文校对"])