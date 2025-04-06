from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .models.base import engine, Base
from .models.user import User
from .models.customer import Customer, CustomerInteraction
from .api import auth, users, customers, agents

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Merchant CRM",
    description="Customer Relationship Management system with AI Agent capabilities",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])

@app.get("/")
async def root():
    return {"message": "Welcome to Merchant CRM API"}

def run():
    """Launched with `poetry run web` at root level"""
    uvicorn.run("merchant.web.main:app", host="0.0.0.0", port=8000, reload=True) 