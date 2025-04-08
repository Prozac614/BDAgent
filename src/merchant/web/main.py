from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import uvicorn
from .models.base import engine, Base
from .models.user import User
from .models.customer import Customer, CustomerInteraction
from .models.email import EmailBinding
from .routes import users, customers, auth, pages, email  # 从routes导入所有路由

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
app.include_router(pages.router, tags=["pages"])  # 添加页面路由
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
app.include_router(email.router, prefix="/api/email", tags=["email"])

@app.get("/")
async def root():
    """根路由，重定向到登录页面"""
    return RedirectResponse(url="/login")

@app.get("/api")
async def api_root():
    """API根路由，返回API信息"""
    return {
        "name": "Merchant CRM API",
        "version": "1.0.0",
        "description": "Customer Relationship Management system with AI Agent capabilities",
        "endpoints": [
            "/api/auth",
            "/api/users",
            "/api/customers",
            "/api/email"
        ],
        "documentation": "/docs"
    }

def run():
    """Launched with `poetry run web` at root level"""
    uvicorn.run("merchant.web.main:app", host="0.0.0.0", port=8000, reload=True) 