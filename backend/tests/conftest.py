import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Set test environment variables
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["AI_API_KEY"] = "test-key"
os.environ["AI_BASE_URL"] = "http://test-ai-api"
os.environ["AI_MODEL_NAME"] = "test-model"

# Import after setting environment
from app.db.database import Base
from app.main import app

# Create test database
engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)