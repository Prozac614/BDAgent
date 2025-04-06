from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..models.base import get_db
from ..services.agent_service import AgentService
from ..schemas.customer import CustomerCreate, CustomerResponse
from ..schemas.agent import ProspectRequest, EngagementRequest, EngagementResponse

router = APIRouter()

@router.post("/prospect", response_model=List[CustomerResponse])
async def prospect_customers(
    request: ProspectRequest,
    db: Session = Depends(get_db)
):
    """使用 Agent 寻找新的潜在客户"""
    try:
        agent_service = AgentService(db)
        customers = await agent_service.prospect_new_customers(
            industry=request.industry,
            region=request.region,
            target_count=request.target_count
        )
        return customers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/engage/{customer_id}", response_model=EngagementResponse)
async def engage_customer(
    customer_id: int,
    request: EngagementRequest,
    db: Session = Depends(get_db)
):
    """使用 Agent 与指定客户进行互动"""
    try:
        agent_service = AgentService(db)
        result = await agent_service.engage_customer(customer_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-customers")
async def analyze_customers(
    db: Session = Depends(get_db)
):
    """使用 Agent 分析所有客户数据并生成见解报告"""
    try:
        agent_service = AgentService(db)
        analysis = await agent_service.analyze_customers()
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 