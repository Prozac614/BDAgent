from fastapi import APIRouter
from .users import router as users_router
from .customers import router as customers_router

# 创建主路由
api_router = APIRouter()

# 添加子路由
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(customers_router, prefix="/customers", tags=["customers"])
