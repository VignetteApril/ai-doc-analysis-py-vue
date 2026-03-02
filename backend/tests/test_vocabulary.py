import pytest
from app.models.vocabulary import Vocabulary

def test_vocabulary_model():
    """Test Vocabulary model creation"""
    vocab = Vocabulary(
        original_word="错误词汇",
        replacement_word="正确词汇",
        weight=5,
        owner_id=1
    )
    
    assert vocab.original_word == "错误词汇"
    assert vocab.replacement_word == "正确词汇"
    assert vocab.weight == 5
    assert vocab.owner_id == 1