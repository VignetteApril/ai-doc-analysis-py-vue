from fastapi import APIRouter
from app.api.v1.endpoints import auth, review, vocabulary

api_router = APIRouter()

# 挂载认证
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
# 挂载公文业务
api_router.include_router(review.router, prefix="/review", tags=["公文校审"])
# 挂载词库管理
api_router.include_router(vocabulary.router, prefix="/vocabulary", tags=["词库管理"])