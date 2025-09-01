#!/bin/bash

# BuildExpenseTracker Development Deployment Script
# This script deploys the application to development environment

set -e  # Exit on any error

echo "🚀 Starting BuildExpenseTracker Development Deployment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v git &> /dev/null; then
        print_error "git is required but not installed"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "python3 is required but not installed"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is required but not installed"
        exit 1
    fi
    
    print_success "All dependencies are available"
}

# Setup backend environment
setup_backend() {
    print_status "Setting up backend environment..."
    
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Check environment variables
    if [ ! -f ".env.development" ]; then
        print_warning "No .env.development file found. Please create one with your Supabase credentials."
        print_status "Required variables: SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, DATABASE_URL"
        exit 1
    fi
    
    # Run seed data if SEED=true
    if [ "${SEED:-false}" = "true" ]; then
        print_status "Running seed data script..."
        python seed_data.py
    fi
    
    cd ..
    print_success "Backend setup completed"
}

# Setup frontend environment
setup_frontend() {
    print_status "Setting up frontend environment..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Check environment variables
    if [ ! -f ".env.development" ]; then
        print_warning "No .env.development file found in frontend. Creating template..."
        cat > .env.development << EOF
VITE_API_BASE_URL=http://localhost:8000
VITE_SUPABASE_URL=your_supabase_url_here
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
EOF
        print_warning "Please update .env.development with your actual values"
    fi
    
    cd ..
    print_success "Frontend setup completed"
}

# Test backend locally
test_backend() {
    print_status "Testing backend locally..."
    
    cd backend
    source venv/bin/activate
    
    # Start backend in background
    uvicorn main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    # Wait for backend to start
    sleep 5
    
    # Test health endpoint
    if curl -f http://localhost:8000/healthz > /dev/null 2>&1; then
        print_success "Backend health check passed"
    else
        print_error "Backend health check failed"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    
    # Test version endpoint
    if curl -f http://localhost:8000/version > /dev/null 2>&1; then
        print_success "Backend version endpoint working"
    else
        print_error "Backend version endpoint failed"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    
    # Stop backend
    kill $BACKEND_PID 2>/dev/null || true
    cd ..
    
    print_success "Backend tests passed"
}

# Build frontend
build_frontend() {
    print_status "Building frontend for development..."
    
    cd frontend
    npm run build
    cd ..
    
    print_success "Frontend build completed"
}

# Display deployment information
show_deployment_info() {
    print_success "Development setup completed!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Set up your Supabase development project"
    echo "2. Update backend/.env.development with your Supabase credentials"
    echo "3. Update frontend/.env.development with your API URL"
    echo "4. Run the schema migration in your Supabase SQL editor:"
    echo "   - Copy contents of backend/supabase_schema.sql"
    echo "   - Paste and run in Supabase SQL Editor"
    echo ""
    echo "🚀 To start development servers:"
    echo "Backend:  cd backend && source venv/bin/activate && uvicorn main:app --reload"
    echo "Frontend: cd frontend && npm run dev"
    echo ""
    echo "🌱 To seed demo data:"
    echo "SEED=true python backend/seed_data.py"
    echo ""
    echo "🔗 Deployment URLs (update these in your deployment platform):"
    echo "Backend:  /healthz, /version endpoints available"
    echo "Frontend: Built and ready for deployment"
}

# Main execution
main() {
    check_dependencies
    setup_backend
    setup_frontend
    test_backend
    build_frontend
    show_deployment_info
}

# Run main function
main
