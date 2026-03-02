import pytest
from app.models.user import User

def test_user_model():
    """Test User model creation"""
    user = User(
        username="testuser",
        hashed_password="hashed_password_placeholder"
    )
    
    assert user.username == "testuser"
    assert user.hashed_password is not None