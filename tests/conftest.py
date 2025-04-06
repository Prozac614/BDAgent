import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from merchant.web.main import app
from merchant.web.models.base import Base, get_db
from merchant.web.models.user import User
from merchant.web.models.customer import Customer, CustomerInteraction

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def test_engine():
    """创建测试数据库引擎"""
    return engine

@pytest.fixture(scope="function")
def test_db():
    """为每个测试创建新的数据库表"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_session(test_db):
    """为每个测试提供数据库会话"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(test_session):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield test_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def superuser_token(client, test_session):
    """创建超级用户并返回token"""
    # 注册超级用户
    response = client.post(
        "/api/auth/register",
        json={
            "email": "admin@example.com",
            "password": "adminpassword",
            "full_name": "Admin User"
        }
    )
    
    # 将用户设置为超级用户
    user = test_session.query(User).filter(User.email == "admin@example.com").first()
    if user:
        user.is_superuser = True
        test_session.commit()
        test_session.refresh(user)
    
    # 登录并返回token
    login_response = client.post(
        "/api/auth/token",
        data={
            "username": "admin@example.com",
            "password": "adminpassword"
        }
    )
    
    # 验证用户确实是超级用户
    user = test_session.query(User).filter(User.email == "admin@example.com").first()
    assert user and user.is_superuser, "Failed to set superuser status"
    
    return login_response.json()["access_token"]

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # 确保所有模型都被导入
    from merchant.web.models.user import User
    from merchant.web.models.customer import Customer, CustomerInteraction
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    yield
    # 清理数据库
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def setup_test_session():
    # 开始事务
    connection = engine.connect()
    transaction = connection.begin()
    
    # 创建测试会话
    session = TestingSessionLocal(bind=connection)
    
    # 替换应用程序的数据库会话
    app.dependency_overrides[get_db] = lambda: session
    
    yield session
    
    # 清理
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session")
def test_engine():
    return engine 