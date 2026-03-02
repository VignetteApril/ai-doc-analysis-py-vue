def test_basic_imports():
    """Test that basic imports work"""
    from app.models.user import User
    from app.models.document import Document, ReviewStatus
    from app.models.vocabulary import Vocabulary
    
    assert User is not None
    assert Document is not None
    assert ReviewStatus is not None
    assert Vocabulary is not None