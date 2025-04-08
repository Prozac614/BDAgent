import pytest
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 设置测试环境变量
os.environ["TESTING"] = "1"

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.merchant.web.main import app
from src.merchant.web.models.base import Base, get_db
from src.merchant.web.models.user import User
from src.merchant.web.models.customer import Customer, CustomerInteraction
from src.merchant.web.models.email import EmailBinding
from src.merchant.web.utils.auth import get_password_hash, create_access_token

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def test_engine():
    """创建测试数据库引擎"""
    return engine

@pytest.fixture(scope="function")
def db():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_session(db):
    """为每个测试提供数据库会话"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(db):
    """创建测试用户"""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_email_binding(db, test_user):
    """创建测试邮箱绑定"""
    binding = EmailBinding(
        user_id=test_user.id,
        email="test@example.com",
        password="testpassword",
        imap_server="imap.example.com",
        imap_port=993
    )
    db.add(binding)
    db.commit()
    db.refresh(binding)
    return binding

@pytest.fixture(scope="function")
def superuser_token(client, db):
    """创建超级用户并返回token"""
    # 创建超级用户
    superuser = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword"),
        full_name="Admin User",
        is_superuser=True,
        is_active=True
    )
    db.add(superuser)
    db.commit()
    db.refresh(superuser)
    
    # 创建访问令牌
    access_token = create_access_token(data={"sub": superuser.email})
    return access_token

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