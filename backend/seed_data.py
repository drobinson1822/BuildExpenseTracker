#!/usr/bin/env python3
"""
Idempotent seed data script for BuildExpenseTracker development environment.
This script can be run multiple times safely - it will only create data if it doesn't exist.
"""

import os
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
env = os.getenv('ENV', 'development')
load_dotenv(f'.env.{env}')

from api.core.database import engine, get_db
from api.models.project import Project
from api.models.forecast import ForecastLineItem
from api.models.expense import ActualExpense
from api.models.draw import DrawTracker

# Demo user ID - in a real deployment, this would be a real user from auth.users
DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"

def create_demo_user_if_not_exists(db: Session):
    """Create a demo user in auth.users table if it doesn't exist"""
    try:
        # Check if demo user exists
        result = db.execute(text("""
            SELECT id FROM auth.users WHERE id = :user_id
        """), {"user_id": DEMO_USER_ID})
        
        if not result.fetchone():
            # Insert demo user
            db.execute(text("""
                INSERT INTO auth.users (
                    id, 
                    email, 
                    encrypted_password, 
                    email_confirmed_at, 
                    created_at, 
                    updated_at,
                    raw_user_meta_data
                ) VALUES (
                    :user_id,
                    'demo@buildexpensetracker.com',
                    '$2a$10$dummy.hash.for.demo.user.only',
                    NOW(),
                    NOW(),
                    NOW(),
                    '{"full_name": "Demo User"}'::jsonb
                )
            """), {"user_id": DEMO_USER_ID})
            print("✅ Created demo user")
        else:
            print("ℹ️  Demo user already exists")
    except Exception as e:
        print(f"⚠️  Could not create demo user (this is normal in local dev): {e}")

def seed_demo_project(db: Session):
    """Create a demo project with forecast items and expenses"""
    
    # Check if demo project already exists
    existing_project = db.query(Project).filter(
        Project.user_id == DEMO_USER_ID,
        Project.name == "Demo House Renovation"
    ).first()
    
    if existing_project:
        print("ℹ️  Demo project already exists")
        return existing_project
    
    # Create demo project
    demo_project = Project(
        user_id=DEMO_USER_ID,
        name="Demo House Renovation",
        address="123 Demo Street, Example City, ST 12345",
        start_date=date.today() - timedelta(days=30),
        target_completion_date=date.today() + timedelta(days=120),
        status="in_progress",
        total_sqft=2500
    )
    
    db.add(demo_project)
    db.flush()  # Get the ID
    
    print(f"✅ Created demo project: {demo_project.name}")
    return demo_project

def seed_forecast_items(db: Session, project: Project):
    """Create forecast line items for the demo project"""
    
    # Check if forecast items already exist
    existing_count = db.query(ForecastLineItem).filter(
        ForecastLineItem.project_id == project.id
    ).count()
    
    if existing_count > 0:
        print(f"ℹ️  {existing_count} forecast items already exist")
        return
    
    forecast_items = [
        {
            "category": "Foundation",
            "estimated_cost": Decimal("15000.00"),
            "unit": "sq ft",
            "notes": "Concrete foundation and footings",
            "status": "Complete",
            "progress_percent": 100
        },
        {
            "category": "Framing",
            "estimated_cost": Decimal("25000.00"),
            "unit": "sq ft",
            "notes": "Lumber framing for walls and roof",
            "status": "Complete",
            "progress_percent": 100
        },
        {
            "category": "Roofing",
            "estimated_cost": Decimal("12000.00"),
            "unit": "sq ft",
            "notes": "Asphalt shingles and underlayment",
            "status": "In Progress",
            "progress_percent": 75
        },
        {
            "category": "Electrical",
            "estimated_cost": Decimal("8500.00"),
            "unit": "outlets",
            "notes": "Wiring, outlets, and electrical panel",
            "status": "In Progress",
            "progress_percent": 60
        },
        {
            "category": "Plumbing",
            "estimated_cost": Decimal("9200.00"),
            "unit": "fixtures",
            "notes": "Pipes, fixtures, and water heater",
            "status": "In Progress",
            "progress_percent": 40
        },
        {
            "category": "HVAC",
            "estimated_cost": Decimal("11000.00"),
            "unit": "system",
            "notes": "Heating and cooling system installation",
            "status": "Not Started",
            "progress_percent": 0
        },
        {
            "category": "Insulation",
            "estimated_cost": Decimal("4500.00"),
            "unit": "sq ft",
            "notes": "Wall and attic insulation",
            "status": "Not Started",
            "progress_percent": 0
        },
        {
            "category": "Drywall",
            "estimated_cost": Decimal("7800.00"),
            "unit": "sq ft",
            "notes": "Drywall installation and finishing",
            "status": "Not Started",
            "progress_percent": 0
        },
        {
            "category": "Flooring",
            "estimated_cost": Decimal("13500.00"),
            "unit": "sq ft",
            "notes": "Hardwood and tile flooring",
            "status": "Not Started",
            "progress_percent": 0
        },
        {
            "category": "Kitchen Cabinets",
            "estimated_cost": Decimal("18000.00"),
            "unit": "linear ft",
            "notes": "Custom kitchen cabinetry",
            "status": "Not Started",
            "progress_percent": 0
        },
        {
            "category": "Bathroom Fixtures",
            "estimated_cost": Decimal("6500.00"),
            "unit": "fixtures",
            "notes": "Toilets, sinks, and shower fixtures",
            "status": "Not Started",
            "progress_percent": 0
        },
        {
            "category": "Interior Paint",
            "estimated_cost": Decimal("3200.00"),
            "unit": "sq ft",
            "notes": "Interior wall and ceiling paint",
            "status": "Not Started",
            "progress_percent": 0
        },
        {
            "category": "Exterior Siding",
            "estimated_cost": Decimal("9800.00"),
            "unit": "sq ft",
            "notes": "Vinyl siding installation",
            "status": "Not Started",
            "progress_percent": 0
        },
        {
            "category": "Windows & Doors",
            "estimated_cost": Decimal("14200.00"),
            "unit": "units",
            "notes": "Energy-efficient windows and doors",
            "status": "Not Started",
            "progress_percent": 0
        },
        {
            "category": "Landscaping",
            "estimated_cost": Decimal("5500.00"),
            "unit": "sq ft",
            "notes": "Basic landscaping and lawn",
            "status": "Not Started",
            "progress_percent": 0
        }
    ]
    
    for item_data in forecast_items:
        forecast_item = ForecastLineItem(
            user_id=DEMO_USER_ID,
            project_id=project.id,
            **item_data
        )
        db.add(forecast_item)
    
    print(f"✅ Created {len(forecast_items)} forecast line items")

def seed_actual_expenses(db: Session, project: Project):
    """Create actual expenses for the demo project"""
    
    # Check if expenses already exist
    existing_count = db.query(ActualExpense).filter(
        ActualExpense.project_id == project.id
    ).count()
    
    if existing_count > 0:
        print(f"ℹ️  {existing_count} actual expenses already exist")
        return
    
    # Get some forecast items to link expenses to
    forecast_items = db.query(ForecastLineItem).filter(
        ForecastLineItem.project_id == project.id
    ).all()
    
    expenses = [
        {
            "vendor": "ABC Concrete Co",
            "amount_spent": Decimal("14800.00"),
            "date": date.today() - timedelta(days=25),
            "forecast_line_item_id": next((f.id for f in forecast_items if f.category == "Foundation"), None)
        },
        {
            "vendor": "Quality Lumber Supply",
            "amount_spent": Decimal("12500.00"),
            "date": date.today() - timedelta(days=20),
            "forecast_line_item_id": next((f.id for f in forecast_items if f.category == "Framing"), None)
        },
        {
            "vendor": "Quality Lumber Supply",
            "amount_spent": Decimal("11200.00"),
            "date": date.today() - timedelta(days=18),
            "forecast_line_item_id": next((f.id for f in forecast_items if f.category == "Framing"), None)
        },
        {
            "vendor": "Superior Roofing Materials",
            "amount_spent": Decimal("8900.00"),
            "date": date.today() - timedelta(days=15),
            "forecast_line_item_id": next((f.id for f in forecast_items if f.category == "Roofing"), None)
        },
        {
            "vendor": "Elite Electric Supply",
            "amount_spent": Decimal("3200.00"),
            "date": date.today() - timedelta(days=12),
            "forecast_line_item_id": next((f.id for f in forecast_items if f.category == "Electrical"), None)
        },
        {
            "vendor": "Pro Plumbing Supplies",
            "amount_spent": Decimal("2800.00"),
            "date": date.today() - timedelta(days=10),
            "forecast_line_item_id": next((f.id for f in forecast_items if f.category == "Plumbing"), None)
        },
        {
            "vendor": "Elite Electric Supply",
            "amount_spent": Decimal("1850.00"),
            "date": date.today() - timedelta(days=8),
            "forecast_line_item_id": next((f.id for f in forecast_items if f.category == "Electrical"), None)
        },
        {
            "vendor": "Home Depot",
            "amount_spent": Decimal("450.00"),
            "date": date.today() - timedelta(days=5),
            "forecast_line_item_id": None  # Miscellaneous expense
        },
        {
            "vendor": "Pro Plumbing Supplies",
            "amount_spent": Decimal("1200.00"),
            "date": date.today() - timedelta(days=3),
            "forecast_line_item_id": next((f.id for f in forecast_items if f.category == "Plumbing"), None)
        },
        {
            "vendor": "Superior Roofing Materials",
            "amount_spent": Decimal("650.00"),
            "date": date.today() - timedelta(days=1),
            "forecast_line_item_id": next((f.id for f in forecast_items if f.category == "Roofing"), None)
        }
    ]
    
    for expense_data in expenses:
        expense = ActualExpense(
            user_id=DEMO_USER_ID,
            project_id=project.id,
            **expense_data
        )
        db.add(expense)
    
    print(f"✅ Created {len(expenses)} actual expenses")

def seed_draw_tracker(db: Session, project: Project):
    """Create draw tracker entry for the demo project"""
    
    # Check if draw tracker already exists
    existing_draw = db.query(DrawTracker).filter(
        DrawTracker.project_id == project.id
    ).first()
    
    if existing_draw:
        print("ℹ️  Draw tracker already exists")
        return
    
    draw_tracker = DrawTracker(
        user_id=DEMO_USER_ID,
        project_id=project.id,
        cash_on_hand=Decimal("25000.00"),
        last_draw_date=date.today() - timedelta(days=15),
        draw_triggered=False,
        notes="Initial construction loan draw completed"
    )
    
    db.add(draw_tracker)
    print("✅ Created draw tracker entry")

def main():
    """Main seeding function"""
    print("🌱 Starting idempotent seed data creation...")
    
    # Check if seeding is enabled
    if os.getenv('SEED') != 'true':
        print("❌ Seeding disabled. Set SEED=true to enable.")
        return
    
    try:
        # Create database session
        db = next(get_db())
        
        # Create demo user (if possible)
        create_demo_user_if_not_exists(db)
        
        # Create demo project
        demo_project = seed_demo_project(db)
        
        # Create forecast items
        seed_forecast_items(db, demo_project)
        
        # Create actual expenses
        seed_actual_expenses(db, demo_project)
        
        # Create draw tracker
        seed_draw_tracker(db, demo_project)
        
        # Commit all changes
        db.commit()
        
        print("🎉 Seed data creation completed successfully!")
        print(f"📊 Demo project ID: {demo_project.id}")
        print(f"👤 Demo user ID: {DEMO_USER_ID}")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
