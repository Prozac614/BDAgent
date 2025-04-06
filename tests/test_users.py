from fastapi.testclient import TestClient
import pytest

from merchant.web.models.user import User

def test_list_users_superuser(client, superuser_token):
    """测试超级用户获取用户列表"""
    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {superuser_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["email"] == "admin@example.com"

def test_list_users_normal_user(client):
    """测试普通用户获取用户列表（应该被拒绝）"""
    # 注册普通用户
    response = client.post(
        "/api/auth/register",
        json={
            "email": "user@example.com",
            "password": "userpassword",
            "full_name": "Normal User"
        }
    )
    token = response.json()["access_token"]
    
    # 尝试获取用户列表
    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough privileges"

def test_create_user_superuser(client, superuser_token):
    """测试超级用户创建新用户"""
    response = client.post(
        "/api/users",
        headers={"Authorization": f"Bearer {superuser_token}"},
        json={
            "email": "newuser@example.com",
            "password": "newpassword",
            "full_name": "New User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"

def test_create_user_normal_user(client):
    """测试普通用户创建新用户（应该被拒绝）"""
    # 注册普通用户
    response = client.post(
        "/api/auth/register",
        json={
            "email": "user@example.com",
            "password": "userpassword",
            "full_name": "Normal User"
        }
    )
    token = response.json()["access_token"]
    
    # 尝试创建新用户
    response = client.post(
        "/api/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "newuser@example.com",
            "password": "newpassword",
            "full_name": "New User"
        }
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough privileges" 