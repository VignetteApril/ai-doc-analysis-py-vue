from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.core.security import SECRET_KEY, ALGORITHM # 确保你的 security.py 有这两个变量

# 定义 OAuth2 方案，告诉 FastAPI 令牌从哪里获取
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证凭证已过期或无效",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解码 JWT 令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 从数据库中查找用户
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    return user