from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..models.base import get_db
from ..models.user import User
from ..models.customer import Customer, CustomerInteraction
from ..schemas.customer import CustomerCreate, CustomerResponse
from ..utils.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[CustomerResponse])
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取客户列表"""
    customers = db.query(Customer).offset(skip).limit(limit).all()
    return customers

@router.post("/", response_model=CustomerResponse)
async def create_customer(
    customer: CustomerCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建新客户"""
    db_customer = db.query(Customer).filter(Customer.email == customer.email).first()
    if db_customer:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    customer_data = customer.dict()
    customer_data["status"] = "potential"  # 设置默认状态为潜在客户
    
    new_customer = Customer(**customer_data, created_by=current_user.id)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取客户详情"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.get("/{customer_id}/interactions")
async def get_customer_interactions(
    customer_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取客户互动记录"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    interactions = db.query(CustomerInteraction)\
        .filter(CustomerInteraction.customer_id == customer_id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return interactions 