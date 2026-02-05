# backend/app/api/v1/auth.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

# 这里定义了 router
router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

# 关键修改：把 @app 改成 @router
@router.post("/login")
async def login(request: LoginRequest):
    if request.username == "admin" and request.password == "123456":
        return {
            "access_token": "mock_jwt_token_for_ai_doc",
            "token_type": "bearer",
            "username": request.username
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="用户名或密码错误"
    )