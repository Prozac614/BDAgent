from typing import List, Optional
from ..models.customer import Customer, CustomerInteraction
from sqlalchemy.orm import Session
import os
import asyncio
from datetime import datetime

class AgentService:
    def __init__(self, db: Session):
        self.db = db
        # 只在非测试环境下初始化 crew
        if not os.getenv("TESTING"):
            from merchant.crew import MerchantCrew
            self.crew = MerchantCrew()
        else:
            self.crew = None

    async def prospect_new_customers(self, industry: str, region: str, target_count: int) -> List[dict]:
        """使用 Agent 来寻找新的潜在客户"""
        if os.getenv("TESTING"):
            # 测试模式下返回模拟数据
            prospects = [
                {
                    "email": "test@example.com",
                    "name": "Test User",
                    "company": "Test Corp",
                    "position": "Test Position"
                }
            ]
        else:
            prospects = await self.crew.find_prospects(industry, region, target_count)
        
        # 将潜在客户保存到数据库
        new_customers = []
        for prospect in prospects:
            customer = Customer(
                email=prospect["email"],
                full_name=prospect["name"],
                company=prospect["company"],
                position=prospect["position"],
                status="prospect",
                notes=f"Auto-generated by Agent. Industry: {industry}, Region: {region}",
                created_at=datetime.now()
            )
            self.db.add(customer)
            new_customers.append(customer)
        
        self.db.commit()
        return new_customers

    async def engage_customer(self, customer_id: int) -> dict:
        """使用 Agent 与现有客户互动"""
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError("Customer not found")

        if os.getenv("TESTING"):
            # 测试模式下返回模拟数据
            interaction = {
                "content": "Test engagement content",
                "subject": "Test subject",
                "next_action": "Test next action"
            }
        else:
            # 使用 Agent 生成互动内容
            interaction = await self.crew.generate_engagement(
                customer_name=customer.full_name,
                company=customer.company,
                history=self._get_customer_history(customer_id)
            )

        # 记录互动
        new_interaction = CustomerInteraction(
            customer_id=customer_id,
            interaction_type="agent_engagement",
            content=interaction["content"],
            created_at=datetime.now()
        )
        self.db.add(new_interaction)
        self.db.commit()

        return {
            "customer_id": customer_id,
            "interaction": interaction,
            "status": "success"
        }

    def _get_customer_history(self, customer_id: int) -> List[dict]:
        """获取客户历史互动记录"""
        interactions = self.db.query(CustomerInteraction)\
            .filter(CustomerInteraction.customer_id == customer_id)\
            .order_by(CustomerInteraction.created_at.desc())\
            .all()
        
        return [
            {
                "type": i.interaction_type,
                "content": i.content,
                "created_at": i.created_at.isoformat()
            }
            for i in interactions
        ] 