from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base


class Vocabulary(Base):
    __tablename__ = "vocabularies"

    id = Column(Integer, primary_key=True, index=True)
    original_word = Column(String(255), nullable=False)    # 原词
    replacement_word = Column(String(255), nullable=False) # 替换词
    weight = Column(Integer, default=1)                    # 权重（越大优先级越高）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))