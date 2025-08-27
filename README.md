# Expense Tracker - Construction Cost Management

A FastAPI-based expense tracking application for construction projects with Supabase backend.

## Database Schema

### Authentication
- Uses Supabase Auth with JWT tokens
- All tables include `user_id` for data isolation
- Row Level Security (RLS) policies ensure users only access their own data

### Tables

#### `projects`
```sql
id SERIAL PRIMARY KEY
user_id UUID NOT NULL REFERENCES auth.users(id)
name VARCHAR NOT NULL
address VARCHAR
start_date DATE
target_completion_date DATE
status VARCHAR DEFAULT 'not_started' -- ('not_started', 'in_progress', 'completed')
total_sqft INTEGER
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
```

#### `forecast_line_items`
```sql
id SERIAL PRIMARY KEY
user_id UUID NOT NULL REFERENCES auth.users(id)
project_id INTEGER NOT NULL REFERENCES projects(id)
category VARCHAR NOT NULL
estimated_cost DECIMAL(10,2) NOT NULL
unit VARCHAR
notes TEXT
progress_percent INTEGER DEFAULT 0 -- (0-100)
status VARCHAR DEFAULT 'Not Started' -- ('Not Started', 'In Progress', 'Complete')
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
```

#### `actual_expenses`
```sql
id SERIAL PRIMARY KEY
user_id UUID NOT NULL REFERENCES auth.users(id)
project_id INTEGER NOT NULL REFERENCES projects(id)
forecast_line_item_id INTEGER REFERENCES forecast_line_items(id)
vendor VARCHAR
amount_spent DECIMAL(10,2) NOT NULL
date DATE
receipt_url VARCHAR
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
```

#### `draw_tracker`
```sql
id SERIAL PRIMARY KEY
user_id UUID NOT NULL REFERENCES auth.users(id)
project_id INTEGER NOT NULL REFERENCES projects(id)
cash_on_hand DECIMAL(10,2) NOT NULL
last_draw_date DATE
draw_triggered BOOLEAN DEFAULT FALSE
notes TEXT
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
```

## Setup

### Environment Variables
Create `.env.development` in the backend directory:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
SUPABASE_ANON_KEY=your-anon-public-key-here
ENV=development
DATABASE_URL=sqlite:///./expense_tracker.db
```

### Supabase Setup
1. Create a new Supabase project
2. Run the SQL from `backend/supabase_schema.sql` in the Supabase SQL Editor
3. This creates all tables with RLS policies for user data isolation

### API Endpoints

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/logout` - Logout user

#### Projects (requires Bearer token)
- `GET /projects` - List user's projects
- `POST /projects` - Create new project
- `GET /projects/{id}` - Get specific project
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

#### Forecast Items (requires Bearer token)
- `GET /forecast` - List forecast items
- `POST /forecast` - Create forecast item
- `PUT /forecast/{id}` - Update forecast item
- `DELETE /forecast/{id}` - Delete forecast item

#### Expenses (requires Bearer token)
- `GET /expenses` - List expenses
- `POST /expenses` - Create expense
- `PUT /expenses/{id}` - Update expense
- `DELETE /expenses/{id}` - Delete expense

#### Draws (requires Bearer token)
- `GET /draws` - List draws
- `POST /draws` - Create draw
- `PUT /draws/{id}` - Update draw
- `DELETE /draws/{id}` - Delete draw

## Security Features
- JWT-based authentication via Supabase
- Row Level Security (RLS) policies on all tables
- User-scoped data access (users only see their own data)
- Service role key used server-side, bypasses RLS with manual user_id filtering