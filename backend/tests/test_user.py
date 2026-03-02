import pytest
from app.models.user import User
from app.core.security import get_password_hash, verify_password

def test_password_hashing():
    """Test password hashing and verification"""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert verify_password(password, hashed) == True
    assert verify_password("wrongpassword", hashed) == False
    assert hashed != password

def test_user_model():
    """Test User model creation"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass")
    )
    
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.hashed_password is not None