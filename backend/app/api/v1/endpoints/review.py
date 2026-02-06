from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Body, Form
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
import os
import uuid
import shutil
import re
import json
import logging

from app.db.database import get_db
from app.models.document import Document, ReviewStatus
from app.models.user import User
from app.api.deps import get_current_user
from app.utils.parser import DocumentParser
from app.utils.exporter import DocumentExporter
from app.services.ai.ai_service import AIService

router = APIRouter()
ai_service = AIService()

UPLOAD_DIR = "uploads/documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 1. 增强版：带搜索和日期过滤的列表接口 [cite: 2026-02-05]
@router.get("/", response_model=dict)
def get_reviews(
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=100),
    name: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """带分页、名称搜索、日期筛选的公文列表 [cite: 2026-02-05]"""
    query = db.query(Document).filter(Document.owner_id == current_user.id)

    # 逻辑过滤：名称模糊查询
    if name:
        query = query.filter(Document.name.contains(name))

    # 逻辑过滤：日期范围
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
                "count": d.review_count
            } for d in docs
        ]
    }

# 2. 修复版：解决 422 报错的上传接口 [cite: 2026-02-05]
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    name: str = Form(...), # ✅ 关键：必须加上这个 Form 字段接收前端传的 name
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """接收文件及名称并存入数据库 [cite: 2026-02-05]"""
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    dest_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_doc = Document(
        name=name, # 使用前端传来的自定义名称
        file_path=dest_path,
        owner_id=current_user.id,
        status=ReviewStatus.PENDING
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
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == doc_id, Document.owner_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="公文未找到")

    doc.content_html = data.get("html")
    db.commit()
    return {"message": "保存成功"}

@router.get("/{doc_id}/download")
async def download_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == doc_id, Document.owner_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="未找到文档")

    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    db.delete(doc)
    db.commit()
    return {"message": "删除成功"}

@router.get("/{doc_id}")
async def get_document_detail(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc_record = db.query(Document).filter(Document.id == doc_id, Document.owner_id == current_user.id).first()
    if not doc_record:
        raise HTTPException(status_code=404, detail="该公文不存在")

    # 1. 如果数据库已经存了 HTML，直接返回
    if doc_record.content_html and doc_record.content_html.strip():
        return {
            "id": doc_record.id,
            "name": doc_record.name,
            "content": doc_record.content_html,
            "status": doc_record.status
        }

    # 2. 如果数据库没有，尝试现场解析物理文件
    if not os.path.exists(doc_record.file_path):
        print(f"❌ 错误：找不到物理文件 {doc_record.file_path}")
        return {"id": doc_record.id, "name": doc_record.name, "content": "<p>错误：物理文件已丢失</p>"}

    try:
        print(f"🔍 正在解析文件: {doc_record.file_path}")
        content_html = DocumentParser.get_content(doc_record.file_path)

        # 调试：检查解析结果
        if not content_html or not content_html.strip():
            print("⚠️ 警告：解析器返回了空字符串")
            content_html = "<p>文档解析失败，内容为空。</p>"
        else:
            # ✅ 关键优化：解析成功后，顺手存入数据库，下次就不用再解析了
            doc_record.content_html = content_html
            db.commit()

        return {
            "id": doc_record.id,
            "name": doc_record.name,
            "content": content_html,
            "status": doc_record.status
        }
    except Exception as e:
        print(f"🔥 解析发生异常: {str(e)}")
        return {"id": doc_record.id, "name": doc_record.name, "content": f"<p>解析异常: {str(e)}</p>"}

@router.post("/{doc_id}/analyze")
async def analyze_document_ai(
    doc_id: int,
    payload: dict = Body(...), # 接收前端传来的 content
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 安全校验 (保持不变)
    doc_record = db.query(Document).filter(
        Document.id == doc_id,
        Document.owner_id == current_user.id
    ).first()

    if not doc_record:
        raise HTTPException(status_code=404, detail="未找到相关文档")

    # 获取 HTML 内容
    content_html = payload.get("content") or doc_record.content_html

    async def event_generator():
        """流式消息生成器"""
        # 初始状态：标记开始
        yield f"data: {json.dumps({'step': 'start', 'desc': '泰山 Agent 已就绪...'})}\n\n"

        # 定义节点描述映射
        step_map = {
            "preprocess": "正在清洗 HTML 并隔离标签...",
            "scan": "初审员扫描中，正在识别潜在错误...",
            "review": "复审员复核中，正在优化语句通顺度...",
            "finalize": "正在将建议重新映射至文档坐标...",
        }

        final_issues = []

        try:
            # 2. 🚀 调用 LangGraph 的异步流
            # astream 会产生类似 {"node_name": {data}} 的字典
            initial_state = {"html_content": content_html, "raw_issues": [], "final_issues": [], "iteration": 0}

            async for event in ai_service.graph.astream(initial_state):
                for node_name, output in event.items():
                    if node_name in step_map:
                        # 发送进度给前端
                        yield f"data: {json.dumps({'step': node_name, 'desc': step_map[node_name], 'status': 'processing'})}\n\n"

                    # 如果是最后一个节点，保存结果
                    if node_name == "finalize":
                        final_issues = output.get("final_issues", [])

            # 3. 任务完成后，更新数据库状态
            doc_record.status = "已校审"
            doc_record.review_count = len(final_issues)
            db.commit()

            # 4. 发送最终结果
            yield f"data: {json.dumps({'step': 'complete', 'results': final_issues})}\n\n"

        except Exception as e:
            logging.error(f"流式分析失败: {str(e)}")
            yield f"data: {json.dumps({'step': 'error', 'desc': '分析中断'})}\n\n"

    # 返回 SSE (Server-Sent Events) 流
    return StreamingResponse(event_generator(), media_type="text/event-stream")