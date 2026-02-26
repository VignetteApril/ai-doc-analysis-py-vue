from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.core.security import verify_password, create_access_token, hash_password
from app.api.deps import get_current_user
from pydantic import BaseModel

router = APIRouter()

# 定义请求模型
class LoginRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    # 1. 在数据库中查找用户
    user = db.query(User).filter(User.username == login_data.username).first()

    # 2. 校验用户是否存在
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 3. 校验密码是否匹配
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 4. 校验账号是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该账号已被禁用"
        )

    # 5. 生成 JWT Token
    access_token = create_access_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username
    }


@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """修改当前登录用户的密码"""
    # 1. 校验原密码
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码不正确"
        )

    # 2. 新密码不能与原密码相同
    if data.old_password == data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码不能与原密码相同"
        )

    # 3. 新密码长度校验
    if len(data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码长度不能少于6位"
        )

    # 4. 更新密码
    current_user.hashed_password = hash_password(data.new_password)
    db.commit()

    return {"message": "密码修改成功"}