from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..models.base import get_db
from ..models.user import User
from ..models.email import EmailBinding
from ..schemas.email import EmailBindRequest, EmailBindResponse, EmailBindingInfo, EmailInboxResponse
from ..utils.auth import get_current_user
from ..utils.email import verify_imap_connection, fetch_inbox_emails

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
        # 检查是否是 Gmail 的不安全登录错误
        if "Gmail 需要应用专用密码" in message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
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

@router.get("/inbox/{binding_id}", response_model=EmailInboxResponse)
async def get_inbox_emails(
    binding_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定邮箱的收件箱邮件"""
    # 获取邮箱绑定信息
    email_binding = db.query(EmailBinding).filter(
        EmailBinding.id == binding_id,
        EmailBinding.user_id == current_user.id
    ).first()
    
    if not email_binding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email binding not found"
        )
    
    try:
        # 获取收件箱邮件
        emails = fetch_inbox_emails(email_binding)
        return EmailInboxResponse(emails=emails, total=len(emails))
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error fetching inbox: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 