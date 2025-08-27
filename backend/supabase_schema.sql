-- Supabase Schema Setup for Expense Tracker
-- Run this in your Supabase SQL Editor

-- Note: auth.users table already has RLS enabled by Supabase

-- Drop existing tables (in correct order due to foreign key constraints)
DROP TABLE IF EXISTS draw_tracker CASCADE;
DROP TABLE IF EXISTS actual_expenses CASCADE;
DROP TABLE IF EXISTS forecast_line_items CASCADE;
DROP TABLE IF EXISTS projects CASCADE;

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    address VARCHAR,
    start_date DATE,
    target_completion_date DATE,
    status VARCHAR DEFAULT 'not_started' CHECK (status IN ('not_started', 'in_progress', 'completed')),
    total_sqft INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Forecast line items table
CREATE TABLE IF NOT EXISTS forecast_line_items (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    category VARCHAR NOT NULL,
    estimated_cost DECIMAL(10,2) NOT NULL,
    unit VARCHAR,
    notes TEXT,
    progress_percent INTEGER DEFAULT 0 CHECK (progress_percent >= 0 AND progress_percent <= 100),
    status VARCHAR DEFAULT 'Not Started' CHECK (status IN ('Not Started', 'In Progress', 'Complete')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Actual expenses table
CREATE TABLE IF NOT EXISTS actual_expenses (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    forecast_line_item_id INTEGER REFERENCES forecast_line_items(id) ON DELETE SET NULL,
    vendor VARCHAR,
    amount_spent DECIMAL(10,2) NOT NULL,
    date DATE,
    receipt_url VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Draw tracker table
CREATE TABLE IF NOT EXISTS draw_tracker (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    cash_on_hand DECIMAL(10,2) NOT NULL,
    last_draw_date DATE,
    draw_triggered BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on all tables
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE forecast_line_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE actual_expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE draw_tracker ENABLE ROW LEVEL SECURITY;

-- RLS Policies for projects
CREATE POLICY "Users can view own projects" ON projects
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can insert own projects" ON projects
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own projects" ON projects
    FOR UPDATE USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can delete own projects" ON projects
    FOR DELETE USING (user_id = auth.uid());

-- RLS Policies for forecast_line_items
CREATE POLICY "Users can view own forecast items" ON forecast_line_items
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can insert own forecast items" ON forecast_line_items
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own forecast items" ON forecast_line_items
    FOR UPDATE USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can delete own forecast items" ON forecast_line_items
    FOR DELETE USING (user_id = auth.uid());

-- RLS Policies for actual_expenses
CREATE POLICY "Users can view own expenses" ON actual_expenses
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can insert own expenses" ON actual_expenses
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own expenses" ON actual_expenses
    FOR UPDATE USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can delete own expenses" ON actual_expenses
    FOR DELETE USING (user_id = auth.uid());

-- RLS Policies for draw_tracker
CREATE POLICY "Users can view own draws" ON draw_tracker
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can insert own draws" ON draw_tracker
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own draws" ON draw_tracker
    FOR UPDATE USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can delete own draws" ON draw_tracker
    FOR DELETE USING (user_id = auth.uid());

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_forecast_line_items_user_id ON forecast_line_items(user_id);
CREATE INDEX IF NOT EXISTS idx_forecast_line_items_project_id ON forecast_line_items(project_id);
CREATE INDEX IF NOT EXISTS idx_actual_expenses_user_id ON actual_expenses(user_id);
CREATE INDEX IF NOT EXISTS idx_actual_expenses_project_id ON actual_expenses(project_id);
CREATE INDEX IF NOT EXISTS idx_draw_tracker_user_id ON draw_tracker(user_id);
CREATE INDEX IF NOT EXISTS idx_draw_tracker_project_id ON draw_tracker(project_id);

-- Updated at triggers (optional but recommended)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_forecast_line_items_updated_at BEFORE UPDATE ON forecast_line_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_actual_expenses_updated_at BEFORE UPDATE ON actual_expenses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_draw_tracker_updated_at BEFORE UPDATE ON draw_tracker
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
