# Supabase Integration Guide

This guide will help you set up and configure Supabase for your Construction Cost Tracker application.

## Prerequisites

1. Python 3.8+
2. pip (Python package manager)
3. A Supabase account (https://supabase.com/)

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Database
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres

# Supabase
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
```

### 3. Set Up Supabase Project

1. Create a new project at https://app.supabase.com/
2. Go to Project Settings > Database to get your connection string
3. Go to Project Settings > API to get your Project URL and keys
4. In the Supabase SQL Editor, run the following SQL to create the required tables:

```sql
-- Create the projects table
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    start_date DATE,
    target_completion_date DATE,
    status TEXT NOT NULL DEFAULT 'not_started',
    total_sqft INTEGER
);

-- Create the forecast_line_items table
CREATE TABLE IF NOT EXISTS forecast_line_items (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    estimated_cost DECIMAL(10, 2) NOT NULL,
    unit TEXT,
    notes TEXT,
    progress_percent INTEGER DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'Not Started'
);

-- Create the actual_expenses table
CREATE TABLE IF NOT EXISTS actual_expenses (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    forecast_line_item_id INTEGER REFERENCES forecast_line_items(id) ON DELETE SET NULL,
    vendor TEXT,
    amount_spent DECIMAL(10, 2) NOT NULL,
    date DATE,
    receipt_url TEXT
);

-- Create the draw_tracker table
CREATE TABLE IF NOT EXISTS draw_tracker (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    cash_on_hand DECIMAL(10, 2) NOT NULL,
    last_draw_date DATE,
    draw_triggered BOOLEAN DEFAULT FALSE,
    notes TEXT
);
```

### 4. Run Migrations (If migrating from SQLite)

If you're migrating from SQLite to Supabase, run:

```bash
python migrate_to_supabase.py
```

### 5. Start the Application

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative API docs: `http://localhost:8000/redoc`

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string for Supabase
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon/public key
- `SUPABASE_SERVICE_KEY`: Your Supabase service role key (for admin operations)
- `SUPABASE_JWT_SECRET`: JWT secret for authentication

## Development

- The application uses SQLAlchemy as the ORM
- Database models are defined in `models.py`
- API routes are defined in `routers.py`
- Database connection is managed in `database.py`
- Supabase client is initialized in `supabase_client.py`

## Deployment

For production deployment, make sure to:
1. Set appropriate CORS origins
2. Use environment variables for all sensitive data
3. Enable SSL for database connections
4. Set up proper database connection pooling

## Troubleshooting

- If you get connection errors, verify your `.env` file has the correct credentials
- Check the Supabase dashboard for any service issues
- Enable debug logging by setting `LOG_LEVEL=DEBUG` in your environment variables
