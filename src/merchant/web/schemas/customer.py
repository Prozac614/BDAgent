from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class CustomerBase(BaseModel):
    email: EmailStr
    full_name: str
    company: str
    position: str
    phone: Optional[str] = None
    notes: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True) 