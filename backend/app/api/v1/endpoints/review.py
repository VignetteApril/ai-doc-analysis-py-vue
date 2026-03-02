from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Body, Form
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
import shutil
import json
import logging

from app.db.database import get_db
from app.models.document import Document, ReviewStatus
from app.models.vocabulary import Vocabulary
from app.models.user import User
from app.api.deps import get_current_user
from app.utils.parser import DocumentParser
from app.utils.exporter import DocumentExporter
from app.services.ai.ai_service import AIService

router = APIRouter()
ai_service = AIService()

UPLOAD_DIR = "uploads/documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/", response_model=dict)
def get_reviews(
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=100),
    name: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Document).filter(Document.owner_id == current_user.id)

    if name:
        query = query.filter(Document.name.contains(name))

    if start_date and end_date:
        query = query.filter(Document.created_at.between(start_date, end_date))

    total = query.count()
    docs = query.order_by(Document.created_at.desc()).offset((page - 1) * size).limit(size).all()

    return {
        "total": total,
        "items": [
            {
                "id": d.id,
                "name": d.name,
                "time": d.created_at.strftime("%Y-%m-%d %H:%M"),
                "status": d.status,
                "lastReview": d.last_review_at.strftime("%Y-%m-%d") if d.last_review_at else None,
                "count": d.review_count,
            }
            for d in docs
        ],
    }


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    dest_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_doc = Document(
        name=name,
        file_path=dest_path,
        owner_id=current_user.id,
        status=ReviewStatus.PENDING,
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    return {"id": new_doc.id, "message": "上传成功"}


@router.post("/{doc_id}/save")
async def save_document(
    doc_id: int,
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter(Document.id == doc_id, Document.owner_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档未找到")

    doc.content_html = data.get("html")
    if doc.content_html and doc.status != ReviewStatus.COMPLETED:
        doc.status = ReviewStatus.COMPLETED
    db.commit()
    return {"message": "保存成功"}


@router.get("/{doc_id}/download")
async def download_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter(Document.id == doc_id, Document.owner_id == current_user.id).first()
    if not doc or not doc.content_html:
        raise HTTPException(status_code=400, detail="文档内容为空")

    export_filename = f"reviewed_{doc.name}"
    export_path = os.path.join("uploads/exports", export_filename)
    os.makedirs("uploads/exports", exist_ok=True)

    success = DocumentExporter.html_to_docx(doc.content_html, export_path)
    if not success:
        raise HTTPException(status_code=500, detail="导出失败")

    return FileResponse(path=export_path, filename=export_filename)


@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter(Document.id == doc_id, Document.owner_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="未找到文档")

    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    db.delete(doc)
    db.commit()
    return {"message": "删除成功"}


@router.get("/{doc_id}")
async def get_document_detail(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc_record = db.query(Document).filter(Document.id == doc_id, Document.owner_id == current_user.id).first()
    if not doc_record:
        raise HTTPException(status_code=404, detail="该公文不存在")

    # Cached HTML exists: try one-time self-heal for table-loss legacy cache.
    if doc_record.content_html and doc_record.content_html.strip():
        cached_html = doc_record.content_html
        try:
            file_path = (doc_record.file_path or "").lower()
            has_table_in_cached_html = "<table" in cached_html.lower()
            should_reparse_table_doc = file_path.endswith(".docx") and (not has_table_in_cached_html)
            if should_reparse_table_doc and DocumentParser._docx_contains_table(doc_record.file_path):
                reparsed_html = DocumentParser.get_content(doc_record.file_path)
                if reparsed_html and reparsed_html.strip():
                    doc_record.content_html = reparsed_html
                    db.commit()
                    cached_html = reparsed_html
        except Exception as exc:
            logging.warning("cached html table reparse skipped: %s", exc)

        return {
            "id": doc_record.id,
            "name": doc_record.name,
            "content": cached_html,
            "status": doc_record.status,
        }

    if not doc_record.file_path or not os.path.exists(doc_record.file_path):
        return {
            "id": doc_record.id,
            "name": doc_record.name,
            "content": "<p>错误：物理文件已丢失</p>",
        }

    try:
        content_html = DocumentParser.get_content(doc_record.file_path)

        if not content_html or not content_html.strip():
            content_html = "<p>文档解析失败，内容为空。</p>"
        else:
            doc_record.content_html = content_html
            db.commit()

        return {
            "id": doc_record.id,
            "name": doc_record.name,
            "content": content_html,
            "status": doc_record.status,
        }
    except Exception as exc:
        return {
            "id": doc_record.id,
            "name": doc_record.name,
            "content": f"<p>解析异常: {str(exc)}</p>",
        }


@router.post("/{doc_id}/reparse")
async def reparse_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc_record = db.query(Document).filter(Document.id == doc_id, Document.owner_id == current_user.id).first()
    if not doc_record:
        raise HTTPException(status_code=404, detail="该公文不存在")

    if not doc_record.file_path or not os.path.exists(doc_record.file_path):
        raise HTTPException(status_code=400, detail="原始文件不存在，无法重解析")

    try:
        content_html = DocumentParser.get_content(doc_record.file_path)
        if not content_html or not content_html.strip():
            raise HTTPException(status_code=500, detail="重解析完成但内容为空")

        doc_record.content_html = content_html
        db.commit()

        return {
            "id": doc_record.id,
            "name": doc_record.name,
            "content": content_html,
            "status": doc_record.status,
            "message": "重解析成功",
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"重解析失败: {str(exc)}")


@router.post("/{doc_id}/analyze")
async def analyze_document_stream(
    doc_id: int,
    payload: dict = Body(..., embed=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc_record = db.query(Document).filter(
        Document.id == doc_id,
        Document.owner_id == current_user.id,
    ).first()

    if not doc_record:
        raise HTTPException(status_code=404, detail="未找到相关文档")

    content_to_analyze = payload.get("content")
    if not content_to_analyze:
        content_to_analyze = doc_record.content_html or ""
        if not content_to_analyze and doc_record.file_path:
            try:
                content_to_analyze = DocumentParser.get_content(doc_record.file_path)
            except Exception:
                pass

    if not content_to_analyze:
        raise HTTPException(status_code=400, detail="文档内容为空，无法分析")

    vocab_items = (
        db.query(Vocabulary)
        .filter(Vocabulary.owner_id == current_user.id)
        .order_by(Vocabulary.weight.desc())
        .all()
    )
    vocabularies = [
        {
            "original_word": v.original_word,
            "replacement_word": v.replacement_word,
            "weight": v.weight,
        }
        for v in vocab_items
    ]

    async def sse_generator():
        try:
            async for chunk in ai_service.analyze_stream(content_to_analyze, vocabularies=vocabularies):
                json_data = json.dumps(chunk, ensure_ascii=False)
                yield f"data: {json_data}\n\n"
        except Exception as exc:
            logging.error("SSE Stream Error: %s", exc)
            err_msg = json.dumps({"step": "error", "desc": "服务器内部错误"}, ensure_ascii=False)
            yield f"data: {err_msg}\n\n"

    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
