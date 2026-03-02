def test_review_imports():
    """Test review module imports"""
    from app.api.v1.endpoints import review
    assert review is not None