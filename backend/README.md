# Construction Cost Tracker - Backend API

A modern, scalable FastAPI backend for managing construction projects, forecasting costs, tracking expenses, and monitoring project progress. Built with a modular architecture using Supabase for authentication and database operations with local PostgreSQL fallback.

## 🏗️ **Architecture Overview**

This backend follows a clean, modular architecture that separates concerns and promotes maintainability:

```
backend/
├── main.py                 # FastAPI application entry point
├── api/                    # Main API module
│   ├── api.py             # Main API router that combines all endpoints
│   ├── core/              # Core functionality
│   │   ├── database.py    # Database configuration and session management
│   │   └── supabase.py    # Supabase client and authentication
│   ├── models/            # Database models (SQLAlchemy)
│   │   ├── base.py        # Base model configuration
│   │   ├── project.py     # Project model and enums
│   │   ├── forecast.py    # Forecast line item model
│   │   ├── expense.py     # Actual expense model
│   │   └── draw.py        # Draw tracker model
│   ├── schemas/           # Pydantic schemas for API validation
│   │   ├── auth.py        # Authentication schemas
│   │   ├── project.py     # Project schemas
│   │   ├── forecast.py    # Forecast schemas
│   │   ├── expense.py     # Expense schemas
│   │   └── draw.py        # Draw tracker schemas
│   └── endpoints/         # API endpoint modules
│       ├── auth.py        # Authentication endpoints
│       ├── projects.py    # Project CRUD operations
│       ├── forecast.py    # Forecast line item operations
│       ├── expenses.py    # Expense tracking operations
│       └── draws.py       # Draw tracker operations
├── tests/                 # Test suite
└── requirements.txt       # Python dependencies
```

## 🚀 **Key Features**

### **Authentication & Security**
- **Supabase JWT Authentication**: Secure token-based authentication
- **User-scoped Data**: All data is filtered by authenticated user
- **Bearer Token Security**: HTTP Bearer authentication on all protected endpoints

### **Database Architecture**
- **Dual Database Support**: Supabase (primary) with local PostgreSQL fallback
- **Connection Pooling**: Optimized database connections with health checks
- **Automatic Migrations**: SQLAlchemy handles database schema creation

### **API Endpoints**

#### **Authentication (`/api/v1/auth`)**
- `POST /register` - User registration with Supabase
- `POST /login` - User authentication with JWT token response
- `POST /refresh` - Token refresh functionality
- `POST /logout` - User logout

#### **Projects (`/api/v1/projects`)**
- `GET /` - List all user projects
- `GET /{project_id}` - Get specific project details
- `POST /` - Create new project
- `PUT /{project_id}` - Update existing project
- `DELETE /{project_id}` - Delete project

#### **Forecast Items (`/api/v1/forecast-items`)**
- `GET /` - List all forecast line items
- `GET /{item_id}` - Get specific forecast item
- `POST /` - Create new forecast item
- `PUT /{item_id}` - Update forecast item
- `DELETE /{item_id}` - Delete forecast item

#### **Expenses (`/api/v1/expenses`)**
- `GET /` - List all actual expenses
- `GET /{expense_id}` - Get specific expense
- `POST /` - Create new expense
- `PUT /{expense_id}` - Update expense
- `DELETE /{expense_id}` - Delete expense

#### **Draw Tracker (`/api/v1/draws`)**
- `GET /` - List all draw records
- `GET /{draw_id}` - Get specific draw record
- `POST /` - Create new draw record
- `PUT /{draw_id}` - Update draw record
- `DELETE /{draw_id}` - Delete draw record

## 📊 **Data Models**

### **Project**
- Basic project information (name, address, dates, status, square footage)
- Relationships to forecast items, expenses, and draw records

### **Forecast Line Item**
- Budget line items with categories, estimated costs, progress tracking
- Links to actual expenses for budget vs. actual analysis

### **Actual Expense**
- Real expenses with vendor information, amounts, dates, receipts
- Optional linking to forecast items for tracking against budget

### **Draw Tracker**
- Cash flow management with draw dates, amounts, and trigger status
- Project-specific financial tracking

## 🛠️ **Setup Instructions**

### **Prerequisites**
- Python 3.9 or higher
- PostgreSQL (optional - for local development)
- Supabase account and project

### **1. Environment Setup**

Create a `.env.development` file in the backend directory:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/expense_tracker

# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SECRET_KEY=your-supabase-service-role-key
SUPABASE_ANON_KEY=your-supabase-anon-key

# Optional Configuration
ENV=development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### **2. Install Dependencies**

```bash
cd backend
pip install -r requirements.txt

# If you encounter issues with pydantic-settings:
pip install pydantic-settings
```

### **3. Database Setup**

#### **Option A: Supabase (Recommended)**
1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Get your project URL and service role key from the API settings
3. Update your `.env.development` file with Supabase credentials
4. The app will automatically create tables on first run

#### **Option B: Local PostgreSQL**
1. Install PostgreSQL locally
2. Create a database: `createdb expense_tracker`
3. Update `DATABASE_URL` in your `.env.development` file
4. Tables will be created automatically on first run

### **4. Run the Application**

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

The API will be available at:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔧 **Development Workflow**

### **Code Structure Guidelines**
- **Models**: Database models in `api/models/` - one file per domain
- **Schemas**: Pydantic validation schemas in `api/schemas/`
- **Endpoints**: API routes in `api/endpoints/` - grouped by functionality
- **Core**: Shared functionality in `api/core/`

### **Adding New Endpoints**
1. Create model in `api/models/`
2. Create schemas in `api/schemas/`
3. Create endpoints in `api/endpoints/`
4. Register router in `api/api.py`
5. Update imports in `__init__.py` files

### **Testing**
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/ -k "auth" -v
python -m pytest tests/ -k "project" -v
```

## 🔒 **Authentication Flow**

1. **Registration**: User registers via `/auth/register`
2. **Login**: User authenticates via `/auth/login` → receives JWT token
3. **Protected Requests**: Include `Authorization: Bearer <token>` header
4. **Token Refresh**: Use `/auth/refresh` to get new tokens
5. **Logout**: Call `/auth/logout` to invalidate session

## 📈 **API Usage Examples**

### **Authentication**
```bash
# Register new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### **Project Management**
```bash
# Create project (with auth token)
curl -X POST "http://localhost:8000/api/v1/projects/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "New House Build", "address": "123 Main St", "total_sqft": 2500}'

# List projects
curl -X GET "http://localhost:8000/api/v1/projects/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🚨 **Error Handling**

The API uses standard HTTP status codes:
- **200**: Success
- **201**: Created
- **204**: No Content (for deletes)
- **400**: Bad Request (validation errors)
- **401**: Unauthorized (authentication required)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found
- **500**: Internal Server Error

## 🔍 **Monitoring & Logging**

- **Health Check**: `/health` endpoint for monitoring
- **Logging**: Comprehensive logging throughout the application
- **Database Monitoring**: Connection pool status and query logging
- **Error Tracking**: Detailed error messages and stack traces

## 🚀 **Deployment**

### **Environment Variables for Production**
```env
ENV=production
DATABASE_URL=postgresql://user:pass@prod-db:5432/expense_tracker
SUPABASE_URL=https://your-prod-project.supabase.co
SUPABASE_SECRET_KEY=your-prod-service-role-key
ALLOWED_ORIGINS=https://your-frontend-domain.com
```

### **Docker Deployment** (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 **Contributing**

1. Follow the modular architecture patterns
2. Add comprehensive tests for new features
3. Update this README for significant changes
4. Use type hints throughout the codebase
5. Follow FastAPI and SQLAlchemy best practices

---

**Built with FastAPI, SQLAlchemy, Supabase, and ❤️**
