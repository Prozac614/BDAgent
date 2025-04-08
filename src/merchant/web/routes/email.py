from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from ..models.base import get_db
from ..models.email import UserEmail, EmailMessage
from ..services.email_service import EmailService
from ..utils.auth import get_current_user

router = APIRouter()

class EmailAccountCreate(BaseModel):
    email_address: str
    password: str
    imap_server: str = "imap.gmail.com"

class EmailMessageResponse(BaseModel):
    id: str
    subject: str
    sender: str
    date: datetime
    content: str
    is_read: bool

    class Config:
        from_attributes = True

@router.post("/connect", response_model=dict)
async def connect_email(
    email_data: EmailAccountCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """绑定邮箱账号"""
    # 检查邮箱是否已经绑定
    existing_email = db.query(UserEmail).filter(
        UserEmail.email_address == email_data.email_address,
        UserEmail.user_id == current_user.id
    ).first()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已经绑定"
        )
    
    # 测试邮箱连接
    email_service = EmailService()
    if not email_service.connect(
        email_data.email_address,
        email_data.password,
        email_data.imap_server
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱连接失败"
        )
    
    # 保存邮箱信息
    user_email = UserEmail(
        user_id=current_user.id,
        email_address=email_data.email_address,
        password=email_data.password,  # 注意：实际应用中应该加密存储
        imap_server=email_data.imap_server
    )
    db.add(user_email)
    db.commit()
    
    return {"message": "邮箱绑定成功"}

@router.get("/inbox", response_model=List[EmailMessageResponse])
async def get_inbox(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取收件箱邮件"""
    # 获取用户的邮箱账号
    user_email = db.query(UserEmail).filter(
        UserEmail.user_id == current_user.id
    ).first()
    
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未绑定邮箱账号"
        )
    
    # 连接邮箱服务器
    email_service = EmailService()
    if not email_service.connect(
        user_email.email_address,
        user_email.password,
        user_email.imap_server
    ):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="邮箱连接失败"
        )
    
    try:
        # 获取邮件
        messages = email_service.get_inbox_messages(limit)
        
        # 更新数据库中的邮件记录
        for msg in messages:
            existing_message = db.query(EmailMessage).filter(
                EmailMessage.message_id == msg.id,
                EmailMessage.user_email_id == user_email.id
            ).first()
            
            if not existing_message:
                email_message = EmailMessage(
                    user_email_id=user_email.id,
                    message_id=msg.id,
                    subject=msg.subject,
                    sender=msg.sender,
                    content=msg.content,
                    is_read=msg.is_read,
                    received_at=msg.date
                )
                db.add(email_message)
        
        db.commit()
        return messages
        
    finally:
        email_service.disconnect() 