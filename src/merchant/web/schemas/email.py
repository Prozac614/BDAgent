from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class EmailBindRequest(BaseModel):
    """邮箱绑定请求"""
    email: EmailStr
    password: str
    imap_server: str = "imap.gmail.com"
    imap_port: int = 993

class EmailBindResponse(BaseModel):
    """邮箱绑定响应"""
    id: int
    email: str
    imap_server: str
    imap_port: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class EmailBindingInfo(BaseModel):
    """邮箱绑定信息"""
    id: int
    email: str
    imap_server: str
    imap_port: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 