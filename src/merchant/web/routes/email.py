from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..models.base import get_db
from ..models.user import User
from ..models.email import EmailBinding
from ..schemas.email import EmailBindRequest, EmailBindResponse, EmailBindingInfo
from ..utils.auth import get_current_user
from ..utils.email import verify_imap_connection

router = APIRouter()

@router.post("/bind", response_model=EmailBindResponse)
async def bind_email(
    email_data: EmailBindRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """绑定邮箱"""
    # 检查邮箱是否已被绑定
    existing_binding = db.query(EmailBinding).filter(EmailBinding.email == email_data.email).first()
    if existing_binding:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already bound"
        )
    
    # 验证IMAP连接
    success, message = verify_imap_connection(
        email=email_data.email,
        password=email_data.password,
        imap_server=email_data.imap_server,
        imap_port=email_data.imap_port
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # 创建邮箱绑定
    email_binding = EmailBinding(
        user_id=current_user.id,
        email=email_data.email,
        password=email_data.password,  # 注意：实际应用中应该加密存储
        imap_server=email_data.imap_server,
        imap_port=email_data.imap_port
    )
    
    db.add(email_binding)
    db.commit()
    db.refresh(email_binding)
    
    return email_binding

@router.get("/list", response_model=List[EmailBindingInfo])
async def list_email_bindings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户绑定的邮箱列表"""
    return db.query(EmailBinding).filter(EmailBinding.user_id == current_user.id).all()

@router.delete("/{binding_id}")
async def unbind_email(
    binding_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """解绑邮箱"""
    binding = db.query(EmailBinding).filter(
        EmailBinding.id == binding_id,
        EmailBinding.user_id == current_user.id
    ).first()
    
    if not binding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email binding not found"
        )
    
    db.delete(binding)
    db.commit()
    
    return {"status": "success", "message": "Email unbound successfully"} 