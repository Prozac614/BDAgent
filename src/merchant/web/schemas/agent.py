from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProspectRequest(BaseModel):
    industry: str
    region: str
    target_count: int = 10

class EngagementRequest(BaseModel):
    context: Optional[str] = None
    custom_instructions: Optional[str] = None

class EngagementResponse(BaseModel):
    customer_id: int
    interaction: dict
    status: str

class CustomerAnalysis(BaseModel):
    customer_id: int
    insights: List[str]
    recommendations: List[str]
    risk_level: str
    next_actions: List[str]

class AnalysisResponse(BaseModel):
    analyses: List[CustomerAnalysis]
    overall_insights: List[str]
    generated_at: datetime 