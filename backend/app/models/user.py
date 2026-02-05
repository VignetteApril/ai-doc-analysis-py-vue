from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    # 存储哈希后的密码，绝对不能存明文
    hashed_password = Column(String, nullable=False)

    # 状态字段
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # 审计记录：创建时间与最后登录时间
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User(username={self.username})>"