from datetime import datetime, timedelta
import os
import re
import shutil
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Body, UploadFile, File
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.vocabulary import Vocabulary
from app.services.ai.ai_service import AIService
from app.utils.parser import DocumentParser

router = APIRouter()
ai_service = AIService()

VOCAB_IMPORT_DIR = "uploads/vocabulary_imports"
os.makedirs(VOCAB_IMPORT_DIR, exist_ok=True)
VOCAB_IMPORT_PREVIEW_TTL_MINUTES = 30
VOCAB_IMPORT_PREVIEWS = {}


def _strip_html_to_text(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html or "")
    return re.sub(r"\s+", " ", text).strip()


def _read_text_file(path: str) -> str:
    for encoding in ("utf-8", "gbk", "latin-1"):
        try:
            with open(path, "r", encoding=encoding) as f:
                return f.read()
        except Exception:
            continue
    return ""


def _extract_plain_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()

    if ext in {".doc", ".docx"}:
        html = DocumentParser.get_content(path)
        return _strip_html_to_text(html)

    if ext in {".txt", ".text"}:
        return _read_text_file(path)

    if ext == ".pdf":
        try:
            import fitz  # PyMuPDF
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"PDF parser unavailable: {exc}")

        text_parts = []
        try:
            with fitz.open(path) as pdf:
                for page in pdf:
                    text_parts.append(page.get_text("text"))
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"PDF parse failed: {exc}")

        return "\n".join(text_parts)

    raise HTTPException(status_code=400, detail="Unsupported file format, only pdf/txt/doc/docx")


def _cleanup_expired_previews():
    now = datetime.utcnow()
    expired_ids = []
    for preview_id, payload in VOCAB_IMPORT_PREVIEWS.items():
        created_at = payload.get("created_at")
        if not isinstance(created_at, datetime):
            expired_ids.append(preview_id)
            continue
        if now - created_at > timedelta(minutes=VOCAB_IMPORT_PREVIEW_TTL_MINUTES):
            expired_ids.append(preview_id)

    for preview_id in expired_ids:
        VOCAB_IMPORT_PREVIEWS.pop(preview_id, None)


def _analyze_pairs_for_import(pairs: list, existing_originals: set) -> tuple[list, int, int]:
    analyzed_items = []
    ready_count = 0
    skipped_count = 0
    seen_originals = set()

    for item in pairs:
        original = str(item.get("original_word", "")).strip()
        replacement = str(item.get("replacement_word", "")).strip()
        reason = "可导入"
        status = "ready"

        if not original or not replacement:
            status = "skip"
            reason = "原词或替换词为空"
        elif original == replacement:
            status = "skip"
            reason = "原词与替换词相同"
        elif original in seen_originals:
            status = "skip"
            reason = "文档内原词重复"
        elif original in existing_originals:
            status = "skip"
            reason = "词库已存在该原词"

        if status == "ready":
            ready_count += 1
            seen_originals.add(original)
        else:
            skipped_count += 1

        analyzed_items.append(
            {
                "original_word": original,
                "replacement_word": replacement,
                "status": status,
                "reason": reason,
            }
        )

    return analyzed_items, ready_count, skipped_count


@router.get("/", response_model=dict)
def get_vocabularies(
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Vocabulary).filter(Vocabulary.owner_id == current_user.id)

    if keyword:
        query = query.filter(
            Vocabulary.original_word.contains(keyword)
            | Vocabulary.replacement_word.contains(keyword)
        )

    if start_date and end_date:
        query = query.filter(Vocabulary.created_at.between(start_date, end_date))

    total = query.count()
    items = query.order_by(Vocabulary.created_at.desc()).offset((page - 1) * size).limit(size).all()

    return {
        "total": total,
        "items": [
            {
                "id": v.id,
                "original_word": v.original_word,
                "replacement_word": v.replacement_word,
                "weight": v.weight,
                "created_at": v.created_at.strftime("%Y-%m-%d %H:%M"),
            }
            for v in items
        ],
    }


@router.post("/", response_model=dict)
def create_vocabulary(
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    original_word = data.get("original_word", "").strip()
    replacement_word = data.get("replacement_word", "").strip()
    weight = data.get("weight", 1)

    if not original_word or not replacement_word:
        raise HTTPException(status_code=400, detail="原词和替换词不能为空")

    existing = db.query(Vocabulary).filter(
        Vocabulary.owner_id == current_user.id,
        Vocabulary.original_word == original_word,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"原词“{original_word}”已存在")

    item = Vocabulary(
        original_word=original_word,
        replacement_word=replacement_word,
        weight=int(weight),
        owner_id=current_user.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return {"id": item.id, "message": "添加成功"}


@router.put("/{vocab_id}", response_model=dict)
def update_vocabulary(
    vocab_id: int,
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(Vocabulary).filter(
        Vocabulary.id == vocab_id,
        Vocabulary.owner_id == current_user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="词条不存在")

    original_word = data.get("original_word", "").strip()
    replacement_word = data.get("replacement_word", "").strip()
    if not original_word or not replacement_word:
        raise HTTPException(status_code=400, detail="原词和替换词不能为空")

    if original_word != item.original_word:
        conflict = db.query(Vocabulary).filter(
            Vocabulary.owner_id == current_user.id,
            Vocabulary.original_word == original_word,
            Vocabulary.id != vocab_id,
        ).first()
        if conflict:
            raise HTTPException(status_code=409, detail=f"原词“{original_word}”已存在")

    item.original_word = original_word
    item.replacement_word = replacement_word
    item.weight = int(data.get("weight", item.weight))
    db.commit()

    return {"message": "更新成功"}


@router.delete("/{vocab_id}", response_model=dict)
def delete_vocabulary(
    vocab_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(Vocabulary).filter(
        Vocabulary.id == vocab_id,
        Vocabulary.owner_id == current_user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="词条不存在")

    db.delete(item)
    db.commit()
    return {"message": "删除成功"}


@router.post("/import", response_model=dict)
async def import_vocabularies(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in {".pdf", ".txt", ".text", ".doc", ".docx"}:
        raise HTTPException(status_code=400, detail="仅支持 pdf/txt/doc/docx")

    tmp_path = os.path.join(VOCAB_IMPORT_DIR, f"{uuid.uuid4()}{ext}")
    try:
        with open(tmp_path, "wb") as out:
            shutil.copyfileobj(file.file, out)

        text_content = _extract_plain_text(tmp_path)
        if not text_content or not text_content.strip():
            raise HTTPException(status_code=400, detail="文档内容为空，无法导入")

        pairs = await ai_service.extract_vocabulary_pairs(text_content)
        if not pairs:
            return {
                "message": "未识别到可导入词条",
                "total_extracted": 0,
                "inserted": 0,
                "skipped": 0,
            }

        existing_rows = db.query(Vocabulary.original_word).filter(Vocabulary.owner_id == current_user.id).all()
        existing_originals = {row[0] for row in existing_rows}
        analyzed_items, _, skipped = _analyze_pairs_for_import(pairs, existing_originals)

        inserted = 0
        for item in analyzed_items:
            if item["status"] != "ready":
                continue
            db.add(
                Vocabulary(
                    original_word=item["original_word"],
                    replacement_word=item["replacement_word"],
                    weight=1,
                    owner_id=current_user.id,
                )
            )
            inserted += 1

        db.commit()

        return {
            "message": "导入完成",
            "total_extracted": len(pairs),
            "inserted": inserted,
            "skipped": skipped,
        }
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass


@router.post("/import/preview", response_model=dict)
async def preview_vocabularies_import(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _cleanup_expired_previews()
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in {".pdf", ".txt", ".text", ".doc", ".docx"}:
        raise HTTPException(status_code=400, detail="仅支持 pdf/txt/doc/docx")

    tmp_path = os.path.join(VOCAB_IMPORT_DIR, f"{uuid.uuid4()}{ext}")
    try:
        with open(tmp_path, "wb") as out:
            shutil.copyfileobj(file.file, out)

        text_content = _extract_plain_text(tmp_path)
        if not text_content or not text_content.strip():
            raise HTTPException(status_code=400, detail="文档内容为空，无法分析")

        pairs = await ai_service.extract_vocabulary_pairs(text_content)
        if not pairs:
            return {
                "message": "未识别到可导入词条",
                "preview_id": None,
                "total_extracted": 0,
                "ready_count": 0,
                "skipped_count": 0,
                "items": [],
            }

        existing_rows = db.query(Vocabulary.original_word).filter(Vocabulary.owner_id == current_user.id).all()
        existing_originals = {row[0] for row in existing_rows}
        analyzed_items, ready_count, skipped_count = _analyze_pairs_for_import(pairs, existing_originals)

        preview_id = str(uuid.uuid4())
        VOCAB_IMPORT_PREVIEWS[preview_id] = {
            "owner_id": current_user.id,
            "created_at": datetime.utcnow(),
            "items": analyzed_items,
        }

        return {
            "message": "分析完成，请确认后导入",
            "preview_id": preview_id,
            "total_extracted": len(analyzed_items),
            "ready_count": ready_count,
            "skipped_count": skipped_count,
            "items": analyzed_items,
        }
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass


@router.post("/import/confirm", response_model=dict)
def confirm_vocabularies_import(
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _cleanup_expired_previews()
    preview_id = str(data.get("preview_id", "")).strip()
    if not preview_id:
        raise HTTPException(status_code=400, detail="preview_id 不能为空")

    preview_payload = VOCAB_IMPORT_PREVIEWS.get(preview_id)
    if not preview_payload:
        raise HTTPException(status_code=404, detail="导入预览不存在或已过期，请重新上传文档")

    if preview_payload.get("owner_id") != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作该导入任务")

    existing_rows = db.query(Vocabulary.original_word).filter(Vocabulary.owner_id == current_user.id).all()
    existing_originals = {row[0] for row in existing_rows}

    selected_items_raw = data.get("selected_items", [])
    if isinstance(selected_items_raw, list) and selected_items_raw:
        source_items = []
        for row in selected_items_raw:
            if not isinstance(row, dict):
                continue
            source_items.append(
                {
                    "original_word": str(row.get("original_word", "")).strip(),
                    "replacement_word": str(row.get("replacement_word", "")).strip(),
                    "status": "ready",
                }
            )
    else:
        selected_originals_raw = data.get("selected_original_words", [])
        selected_originals = None
        if isinstance(selected_originals_raw, list) and selected_originals_raw:
            selected_originals = {str(i).strip() for i in selected_originals_raw if str(i).strip()}

        source_items = []
        for item in preview_payload.get("items", []):
            if item.get("status") != "ready":
                continue
            original = str(item.get("original_word", "")).strip()
            if selected_originals is not None and original not in selected_originals:
                continue
            source_items.append(item)

    inserted = 0
    skipped = 0
    seen_originals = set()
    for item in source_items:
        original = str(item.get("original_word", "")).strip()
        replacement = str(item.get("replacement_word", "")).strip()

        if not original or not replacement or original == replacement:
            skipped += 1
            continue
        if len(original) < 2 or len(replacement) < 2:
            skipped += 1
            continue
        if original in seen_originals:
            skipped += 1
            continue
        if original in existing_originals:
            skipped += 1
            continue

        db.add(
            Vocabulary(
                original_word=original,
                replacement_word=replacement,
                weight=1,
                owner_id=current_user.id,
            )
        )
        seen_originals.add(original)
        existing_originals.add(original)
        inserted += 1

    db.commit()
    VOCAB_IMPORT_PREVIEWS.pop(preview_id, None)

    return {
        "message": "导入完成",
        "inserted": inserted,
        "skipped": skipped,
    }


@router.get("/all", response_model=list)
def get_all_vocabularies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = db.query(Vocabulary).filter(
        Vocabulary.owner_id == current_user.id
    ).order_by(Vocabulary.weight.desc()).all()

    return [
        {
            "id": v.id,
            "original_word": v.original_word,
            "replacement_word": v.replacement_word,
            "weight": v.weight,
        }
        for v in items
    ]
