# Merchant CRM

一个基于 FastAPI 和 crewAI 的智能客户关系管理系统。

## 功能特点

- 用户认证与授权
- 客户管理
- AI 驱动的客户开发
- 智能客户互动
- 自动化邮件沟通

## 系统要求

- Python >= 3.10, < 3.13
- SQLite3

## 安装

1. 克隆项目：

```bash
git clone [项目地址]
cd merchant
```

2. 创建并激活虚拟环境：

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
```

3. 安装依赖：

```bash
pip install -e .
```

4. 配置环境变量：

复制 `.env.example` 到 `.env` 并填写必要的配置：

```env
# API Keys
DEEPSEEK_API_KEY=your_api_key
SERPER_API_KEY=your_api_key

# Database configuration
DATABASE_URL=sqlite:///./merchant.db

# Email configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
EMAIL_SENDER=your-crm@example.com
```

## 启动服务

使用以下命令启动开发服务器：

```bash
uvicorn merchant.web.main:app --host 0.0.0.0 --port 8000 --reload
```

服务器将在 http://localhost:8000 启动，你可以通过以下方式访问：

- API 文档：http://localhost:8000/docs
- API 端点：http://localhost:8000/api

## API 端点

- 认证
  - POST /api/auth/register - 注册新用户
  - POST /api/auth/token - 用户登录
  - GET /api/auth/me - 获取当前用户信息

- 用户管理
  - GET /api/users - 获取用户列表
  - POST /api/users - 创建新用户

- 客户管理
  - GET /api/customers - 获取客户列表
  - POST /api/customers - 创建新客户
  - GET /api/customers/{id} - 获取客户详情
  - GET /api/customers/{id}/interactions - 获取客户互动记录

- AI 代理
  - POST /api/agents/prospect - 智能寻找潜在客户
  - POST /api/agents/engage/{customer_id} - AI 驱动的客户互动
  - POST /api/agents/analyze-customers - 分析客户数据生成见解
