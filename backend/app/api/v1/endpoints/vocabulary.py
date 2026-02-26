from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.models.vocabulary import Vocabulary
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=dict)
def get_vocabularies(
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """带分页、关键词搜索（原词/替换词）、日期筛选的词库列表"""
    query = db.query(Vocabulary).filter(Vocabulary.owner_id == current_user.id)

    if keyword:
        query = query.filter(
            Vocabulary.original_word.contains(keyword) |
            Vocabulary.replacement_word.contains(keyword)
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
                "created_at": v.created_at.strftime("%Y-%m-%d %H:%M")
            } for v in items
        ]
    }


@router.post("/", response_model=dict)
def create_vocabulary(
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """新增替换词条"""
    original_word = data.get("original_word", "").strip()
    replacement_word = data.get("replacement_word", "").strip()
    weight = data.get("weight", 1)

    if not original_word or not replacement_word:
        raise HTTPException(status_code=400, detail="原词和替换词不能为空")

    # 防止同一用户重复添加同一原词
    existing = db.query(Vocabulary).filter(
        Vocabulary.owner_id == current_user.id,
        Vocabulary.original_word == original_word
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"原词「{original_word}」已存在")

    item = Vocabulary(
        original_word=original_word,
        replacement_word=replacement_word,
        weight=int(weight),
        owner_id=current_user.id
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
    current_user: User = Depends(get_current_user)
):
    """修改替换词条"""
    item = db.query(Vocabulary).filter(
        Vocabulary.id == vocab_id,
        Vocabulary.owner_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="词条不存在")

    original_word = data.get("original_word", "").strip()
    replacement_word = data.get("replacement_word", "").strip()
    if not original_word or not replacement_word:
        raise HTTPException(status_code=400, detail="原词和替换词不能为空")

    # 若原词被修改，检查是否与其他词条冲突
    if original_word != item.original_word:
        conflict = db.query(Vocabulary).filter(
            Vocabulary.owner_id == current_user.id,
            Vocabulary.original_word == original_word,
            Vocabulary.id != vocab_id
        ).first()
        if conflict:
            raise HTTPException(status_code=409, detail=f"原词「{original_word}」已存在")

    item.original_word = original_word
    item.replacement_word = replacement_word
    item.weight = int(data.get("weight", item.weight))
    db.commit()

    return {"message": "更新成功"}


@router.delete("/{vocab_id}", response_model=dict)
def delete_vocabulary(
    vocab_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除词条"""
    item = db.query(Vocabulary).filter(
        Vocabulary.id == vocab_id,
        Vocabulary.owner_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="词条不存在")

    db.delete(item)
    db.commit()
    return {"message": "删除成功"}


@router.get("/all", response_model=list)
def get_all_vocabularies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户全部词条（供 AI 分析时使用）"""
    items = db.query(Vocabulary).filter(
        Vocabulary.owner_id == current_user.id
    ).order_by(Vocabulary.weight.desc()).all()

    return [
        {
            "id": v.id,
            "original_word": v.original_word,
            "replacement_word": v.replacement_word,
            "weight": v.weight
        } for v in items
    ]