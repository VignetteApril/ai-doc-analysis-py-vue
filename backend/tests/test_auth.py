def test_auth_imports():
    """Test auth module imports"""
    from app.api.v1.endpoints import auth
    assert auth is not None