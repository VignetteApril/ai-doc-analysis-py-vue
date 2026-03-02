import pytest
from app.models.document import Document, ReviewStatus

def test_document_model():
    """Test Document model creation"""
    doc = Document(
        name="test_document.docx",
        file_path="/tmp/test_document.docx",
        owner_id=1,
        status=ReviewStatus.PENDING
    )
    
    assert doc.name == "test_document.docx"
    assert doc.file_path == "/tmp/test_document.docx"
    assert doc.owner_id == 1
    assert doc.status == ReviewStatus.PENDING

def test_document_status_enum():
    """Test ReviewStatus enum values"""
    assert ReviewStatus.PENDING == "未校审"
    assert ReviewStatus.REVIEWING == "校审中"
    assert ReviewStatus.COMPLETED == "已校审"