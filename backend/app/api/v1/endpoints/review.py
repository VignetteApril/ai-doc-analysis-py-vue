from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
import shutil

from app.db.database import get_db
from app.models.document import Document, ReviewStatus
from app.models.user import User
from app.api.deps import get_current_user # 假设你已写好 JWT 校验依赖

router = APIRouter()

# 存储路径配置
UPLOAD_DIR = "uploads/documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=List[dict])
def get_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的公文列表"""
    docs = db.query(Document).filter(Document.owner_id == current_user.id).order_by(Document.created_at.desc()).all()
    return [
        {
            "id": d.id,
            "name": d.name,
            "time": d.created_at.strftime("%Y-%m-%d"),
            "status": d.status,
            "lastReview": d.last_review_at.strftime("%Y-%m-%d") if d.last_review_at else None,
            "count": d.review_count
        } for d in docs
    ]

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """接收文件并存入数据库"""
    # 1. 生成唯一文件名防止覆盖
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    dest_path = os.path.join(UPLOAD_DIR, unique_filename)

    # 2. 保存文件到磁盘
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. 记录到数据库
    new_doc = Document(
        name=file.filename,
        file_path=dest_path,
        owner_id=current_user.id,
        status=ReviewStatus.PENDING
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    return {"id": new_doc.id, "message": "上传成功，准备校审"}