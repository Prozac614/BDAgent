import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import imaplib

from src.merchant.web.main import app
from src.merchant.web.models.email import EmailBinding
from src.merchant.web.models.user import User
from src.merchant.web.utils.email import verify_imap_connection
from src.merchant.web.utils.auth import create_access_token

client = TestClient(app)

def get_test_token(user: User) -> str:
    """获取测试用户的access token"""
    access_token = create_access_token(data={"sub": user.email})
    return f"Bearer {access_token}"

def test_verify_imap_connection_success():
    """测试IMAP连接验证成功的情况"""
    with patch('imaplib.IMAP4_SSL') as mock_imap:
        # 配置mock对象
        mock_imap_instance = MagicMock()
        mock_imap.return_value = mock_imap_instance
        
        # 调用函数
        success, message = verify_imap_connection(
            email="test@example.com",
            password="password123",
            imap_server="imap.example.com",
            imap_port=993
        )
        
        # 验证结果
        assert success is True
        assert message == "Connection successful"
        mock_imap_instance.login.assert_called_once_with("test@example.com", "password123")
        mock_imap_instance.logout.assert_called_once()

def test_verify_imap_connection_failure():
    """测试IMAP连接验证失败的情况"""
    with patch('imaplib.IMAP4_SSL') as mock_imap:
        # 配置mock对象抛出异常
        mock_imap_instance = MagicMock()
        mock_imap_instance.login.side_effect = Exception("Connection failed")
        mock_imap.return_value = mock_imap_instance
        
        # 调用函数
        success, message = verify_imap_connection(
            email="test@example.com",
            password="wrong_password",
            imap_server="imap.example.com",
            imap_port=993
        )
        
        # 验证结果
        assert success is False
        assert "Connection failed" in message

@pytest.fixture
def test_user(db: Session):
    """创建测试用户"""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_email_binding(db: Session, test_user: User):
    """创建测试邮箱绑定"""
    binding = EmailBinding(
        user_id=test_user.id,
        email="bound@example.com",
        password="password123",
        imap_server="imap.example.com",
        imap_port=993
    )
    db.add(binding)
    db.commit()
    db.refresh(binding)
    return binding

def test_bind_email_success(client: TestClient, test_user: User, db: Session):
    """测试邮箱绑定成功的情况"""
    with patch('imaplib.IMAP4_SSL') as mock_imap:
        # 配置mock对象
        mock_imap_instance = MagicMock()
        mock_imap.return_value = mock_imap_instance
        
        # 发送请求
        response = client.post(
            "/api/email/bind",
            json={
                "email": "new@example.com",
                "password": "password123",
                "imap_server": "imap.example.com",
                "imap_port": 993
            },
            headers={"Authorization": get_test_token(test_user)}
        )

        # 验证结果
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content.decode()}")
        assert response.status_code == 200
        assert response.json()["email"] == "new@example.com"

def test_bind_email_duplicate(client: TestClient, test_user: User, test_email_binding: EmailBinding):
    """测试绑定重复邮箱的情况"""
    response = client.post(
        "/api/email/bind",
        json={
            "email": test_email_binding.email,
            "password": "password123",
            "imap_server": "imap.example.com",
            "imap_port": 993
        },
        headers={"Authorization": get_test_token(test_user)}
    )

    assert response.status_code == 400

def test_list_email_bindings(client: TestClient, test_user: User, test_email_binding: EmailBinding):
    """测试获取邮箱绑定列表"""
    response = client.get(
        "/api/email/list",
        headers={"Authorization": get_test_token(test_user)}
    )

    assert response.status_code == 200

def test_unbind_email_success(client: TestClient, test_user: User, test_email_binding: EmailBinding, db: Session):
    """测试解绑邮箱成功的情况"""
    binding_id = test_email_binding.id  # 保存ID以供后续查询使用
    
    response = client.delete(
        f"/api/email/{binding_id}",
        headers={"Authorization": get_test_token(test_user)}
    )

    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content.decode()}")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # 验证数据库中已删除
    db.commit()  # 提交事务以确保删除生效
    binding = db.query(EmailBinding).filter(EmailBinding.id == binding_id).first()
    assert binding is None

def test_unbind_email_not_found(client: TestClient, test_user: User):
    """测试解绑不存在的邮箱"""
    response = client.delete(
        "/api/email/999",
        headers={"Authorization": get_test_token(test_user)}
    )

    assert response.status_code == 404 