from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from merchant.web.main import app
from merchant.web.models.base import Base
from merchant.web.models.user import User
from merchant.web.utils.auth import get_db

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite://"  # 使用内存数据库
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    # 创建测试数据库表
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # 清理数据库
    Base.metadata.drop_all(bind=engine)

def test_register(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

def test_login(client):
    # First register a user
    client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword",
            "full_name": "Test User"
        }
    )
    
    # Then try to login
    response = client.post(
        "/api/auth/token",
        data={
            "username": "test@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

def test_get_current_user(client):
    # First register and login
    client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword",
            "full_name": "Test User"
        }
    )
    
    login_response = client.post(
        "/api/auth/token",
        data={
            "username": "test@example.com",
            "password": "testpassword"
        }
    )
    token = login_response.json()["access_token"]
    
    # Then get current user info
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"

def test_register_duplicate_email(client):
    """测试注册重复邮箱"""
    # 第一次注册
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    
    # 尝试使用相同邮箱再次注册
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "anotherpassword",
            "full_name": "Another User"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_wrong_password(client):
    """测试使用错误密码登录"""
    # 先注册用户
    client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword",
            "full_name": "Test User"
        }
    )
    
    # 尝试使用错误密码登录
    response = client.post(
        "/api/auth/token",
        data={
            "username": "test@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_get_current_user_invalid_token(client):
    """测试使用无效token获取用户信息"""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials" 