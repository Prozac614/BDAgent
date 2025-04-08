from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

class EmailBinding(Base):
    """用户邮箱绑定"""
    __tablename__ = "email_bindings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)  # 注意：实际应用中应该加密存储
    imap_server = Column(String, default="imap.gmail.com")
    imap_port = Column(Integer, default=993)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="email_bindings") 