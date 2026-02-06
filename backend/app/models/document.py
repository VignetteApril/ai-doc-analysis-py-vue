from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class ReviewStatus(str, enum.Enum):
    PENDING = "未校审"
    REVIEWING = "校审中"
    COMPLETED = "已校审"

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)  # 存储在磁盘上的路径
    content_html = Column(Text, nullable=True)
    status = Column(String(20), default=ReviewStatus.PENDING)
    review_count = Column(Integer, default=0)
    last_review_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联用户
    owner_id = Column(Integer, ForeignKey("users.id"))