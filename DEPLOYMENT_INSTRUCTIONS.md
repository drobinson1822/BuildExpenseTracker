# BuildExpenseTracker - Development Deployment Instructions

This guide will walk you through deploying BuildExpenseTracker to development environment, **skipping indexing** but **including idempotent seed data** as requested.

## Prerequisites

- [Supabase](https://supabase.com) account
- [Render](https://render.com) or [Fly.io](https://fly.io) account for backend
- [Vercel](https://vercel.com) or [Netlify](https://netlify.com) account for frontend
- Git repository pushed to GitHub

## Step 1: Set Up Supabase Development Project

1. **Create Supabase Project**
   - Go to [Supabase Dashboard](https://supabase.com/dashboard)
   - Click "New Project"
   - Name: `build-expense-tracker-dev`
   - Choose a region close to you
   - Set a strong database password

2. **Apply Schema (Skip Indexing)**
   - Go to SQL Editor in your Supabase dashboard
   - Copy the contents of `backend/supabase_schema.sql`
   - **Remove or comment out the index creation lines (127-134):**
     ```sql
     -- Skip these lines as requested:
     -- CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
     -- CREATE INDEX IF NOT EXISTS idx_forecast_line_items_user_id ON forecast_line_items(user_id);
     -- CREATE INDEX IF NOT EXISTS idx_forecast_line_items_project_id ON forecast_line_items(project_id);
     -- CREATE INDEX IF NOT EXISTS idx_actual_expenses_user_id ON actual_expenses(user_id);
     -- CREATE INDEX IF NOT EXISTS idx_actual_expenses_project_id ON actual_expenses(project_id);
     -- CREATE INDEX IF NOT EXISTS idx_draw_tracker_user_id ON draw_tracker(user_id);
     -- CREATE INDEX IF NOT EXISTS idx_draw_tracker_project_id ON draw_tracker(project_id);
     ```
   - Run the modified SQL

3. **Get Supabase Credentials**
   - Go to Settings → API
   - Copy these values:
     - Project URL
     - `anon` `public` key
     - `service_role` `secret` key
   - Go to Settings → Database
   - Copy the connection string (URI format)

## Step 2: Deploy Backend API

### Option A: Deploy to Render

1. **Connect Repository**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select the repository: `BuildExpenseTracker`

2. **Configure Service**
   - Name: `buildexpensetracker-api-dev`
   - Branch: `dev` (or `main` if you don't have a dev branch)
   - Root Directory: `backend`
   - Runtime: `Docker`
   - Dockerfile Path: `./Dockerfile`

3. **Set Environment Variables**
   ```
   ENV=development
   SEED=true
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   DATABASE_URL=your_supabase_database_url
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,https://your-frontend-domain.vercel.app
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Note the service URL (e.g., `https://buildexpensetracker-api-dev.onrender.com`)

### Option B: Deploy to Fly.io

1. **Install Fly CLI**
   ```bash
   # macOS
   brew install flyctl
   
   # Or download from https://fly.io/docs/hands-on/install-flyctl/
   ```

2. **Login and Deploy**
   ```bash
   cd backend
   fly auth login
   fly launch --dockerfile Dockerfile --name buildexpensetracker-api-dev
   ```

3. **Set Secrets**
   ```bash
   fly secrets set SUPABASE_URL="your_supabase_project_url"
   fly secrets set SUPABASE_ANON_KEY="your_supabase_anon_key"
   fly secrets set SUPABASE_SERVICE_ROLE_KEY="your_supabase_service_role_key"
   fly secrets set DATABASE_URL="your_supabase_database_url"
   fly secrets set ALLOWED_ORIGINS="http://localhost:3000,http://localhost:5173,https://your-frontend-domain.vercel.app"
   ```

4. **Deploy**
   ```bash
   fly deploy
   ```

## Step 3: Seed Demo Data

After your backend is deployed and running:

1. **Verify Backend Health**
   - Visit `https://your-backend-url.onrender.com/healthz`
   - Should return `{"status": "ok", ...}`

2. **Seed Data Automatically**
   - The seed data will run automatically because `SEED=true` is set
   - Check your Supabase dashboard → Table Editor to verify data was created
   - You should see:
     - 1 demo project: "Demo House Renovation"
     - 15 forecast line items
     - 10 actual expenses
     - 1 draw tracker entry

## Step 4: Deploy Frontend

### Option A: Deploy to Vercel

1. **Connect Repository**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Project**
   - Framework Preset: `Vite`
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`

3. **Set Environment Variables**
   ```
   VITE_API_BASE=https://your-backend-url.onrender.com/api/v1
   VITE_SUPABASE_URL=your_supabase_project_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

4. **Deploy**
   - Click "Deploy"
   - Note the deployment URL

### Option B: Deploy to Netlify

1. **Connect Repository**
   - Go to [Netlify Dashboard](https://app.netlify.com)
   - Click "New site from Git"
   - Connect your GitHub repository

2. **Configure Build**
   - Base directory: `frontend`
   - Build command: `npm ci && npm run build`
   - Publish directory: `frontend/dist`

3. **Set Environment Variables**
   - Go to Site settings → Environment variables
   - Add the same variables as Vercel option above

## Step 5: Update CORS Settings

1. **Update Backend CORS**
   - Go back to your backend deployment (Render/Fly.io)
   - Update the `ALLOWED_ORIGINS` environment variable
   - Add your frontend URL: `https://your-frontend-url.vercel.app`
   - Redeploy the backend

## Step 6: Test Your Deployment

1. **Test Backend Endpoints**
   ```bash
   # Health check
   curl https://your-backend-url.onrender.com/healthz
   
   # Version info
   curl https://your-backend-url.onrender.com/version
   
   # List projects (should return demo project)
   curl https://your-backend-url.onrender.com/api/v1/projects
   ```

2. **Test Frontend**
   - Visit your frontend URL
   - Try to register/login
   - Navigate through the application
   - Verify the demo project appears

## Step 7: Local Development Setup

To continue development locally:

1. **Create Environment Files**
   ```bash
   # Backend
   cp env.template backend/.env.development
   # Edit backend/.env.development with your Supabase credentials
   
   # Frontend  
   cp env.template frontend/.env.development
   # Edit frontend/.env.development with your API URL
   ```

2. **Run Development Servers**
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   
   # Frontend (in another terminal)
   cd frontend
   npm install
   npm run dev
   ```

## Troubleshooting

### Backend Issues
- Check logs in Render/Fly.io dashboard
- Verify all environment variables are set
- Test `/healthz` endpoint

### Frontend Issues
- Check browser console for errors
- Verify `VITE_API_BASE` points to correct backend URL
- Check network tab for failed API calls

### Database Issues
- Verify Supabase connection string is correct
- Check RLS policies are applied
- Ensure demo user exists in auth.users table

## Next Steps

1. **Set up CI/CD** - The GitHub Actions workflow is already configured
2. **Add monitoring** - Consider adding Sentry for error tracking
3. **Custom domain** - Set up custom domains for both frontend and backend
4. **Production deployment** - Follow similar steps for production environment

---

Your BuildExpenseTracker development environment is now deployed with:
- ✅ Supabase database with schema (no indexes as requested)
- ✅ Idempotent seed data with demo project
- ✅ Backend API with health/version endpoints
- ✅ Frontend application
- ✅ CORS configured for cross-origin requests
