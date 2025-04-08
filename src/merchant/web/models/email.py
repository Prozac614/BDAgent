from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

class UserEmail(Base):
    """用户邮箱账号"""
    __tablename__ = "user_emails"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email_address = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)  # 注意：实际应用中应该加密存储
    imap_server = Column(String(255), default="imap.gmail.com")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="emails")
    messages = relationship("EmailMessage", back_populates="user_email", cascade="all, delete-orphan")

class EmailMessage(Base):
    """邮件消息"""
    __tablename__ = "email_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_email_id = Column(Integer, ForeignKey("user_emails.id"), nullable=False)
    message_id = Column(String(255), nullable=False)
    subject = Column(String(255))
    sender = Column(String(255))
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    received_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user_email = relationship("UserEmail", back_populates="messages") 