import os
import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from main import app
from models import Base
from database import engine

# Use a temporary SQLite DB for tests
test_db_fd, test_db_path = tempfile.mkstemp()
os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path}"
Base.metadata.create_all(bind=engine)
client = TestClient(app)

def teardown_module(module):
    os.close(test_db_fd)
    os.unlink(test_db_path)

@pytest.fixture(scope="module")
def ids():
    return {}

def test_full_flow(ids):
    # Create Project
    payload = {
        "name": "Test Project",
        "address": "123 Main St",
        "start_date": "2025-08-01",
        "target_completion_date": "2025-12-31",
        "status": "Planned",
        "total_sqft": 2500
    }
    r = client.post("/api/projects/", json=payload)
    print("Create Project Response:", r.status_code, r.json())
    assert r.status_code == 200
    ids["project_id"] = r.json()["id"]

    # Create Forecast Line Item
    payload = {
        "project_id": ids["project_id"],
        "category": "Framing Labor",
        "estimated_cost": 20000,
        "unit": "lump sum",
        "notes": "Includes all framing",
        "progress_percent": 0,
        "status": "Not Started"
    }
    r = client.post("/api/forecast-items/", json=payload)
    print("Create ForecastLineItem Response:", r.status_code, r.json())
    assert r.status_code == 200
    ids["forecast_id"] = r.json()["id"]

    # Create Actual Expense
    payload = {
        "project_id": ids["project_id"],
        "forecast_line_item_id": ids["forecast_id"],
        "vendor": "ABC Framing",
        "amount_spent": 5000,
        "date": "2025-08-10",
        "receipt_url": None
    }
    r = client.post("/api/expenses/", json=payload)
    print("Create ActualExpense Response:", r.status_code, r.json())
    if r.status_code != 200:
        print("Expense creation error detail:", r.json())
    assert r.status_code == 200
    ids["expense_id"] = r.json()["id"]

    # Create Draw
    payload = {
        "project_id": ids["project_id"],
        "cash_on_hand": 15000,
        "last_draw_date": "2025-08-11",
        "draw_triggered": False,
        "notes": "Initial draw"
    }
    r = client.post("/api/draws/", json=payload)
    print("Create Draw Response:", r.status_code, r.json())
    assert r.status_code == 200
    ids["draw_id"] = r.json()["id"]

    # E2E: Get, update, and delete
    r = client.get(f"/api/projects/{ids['project_id']}")
    print("Get Project Response:", r.status_code, r.json())
    assert r.status_code == 200

    r = client.get("/api/forecast-items/")
    print("List ForecastItems Response:", r.status_code, r.json())
    assert r.status_code == 200

    r = client.get("/api/expenses/")
    print("List Expenses Response:", r.status_code, r.json())
    assert r.status_code == 200

    r = client.get("/api/draws/")
    print("List Draws Response:", r.status_code, r.json())
    assert r.status_code == 200

    # Update forecast progress
    r = client.put(f"/api/forecast-items/{ids['forecast_id']}", json={
        "project_id": ids["project_id"],
        "category": "Framing Labor",
        "estimated_cost": 20000,
        "unit": "lump sum",
        "notes": "Includes all framing",
        "progress_percent": 50,
        "status": "In Progress"
    })
    print("Update ForecastLineItem Response:", r.status_code, r.json())
    assert r.status_code == 200
    assert r.json()["progress_percent"] == 50

    # Delete expense
    r = client.delete(f"/api/expenses/{ids['expense_id']}")
    print("Delete Expense Response:", r.status_code, r.json())
    assert r.status_code == 200
    # Delete forecast item
    r = client.delete(f"/api/forecast-items/{ids['forecast_id']}")
    print("Delete ForecastItem Response:", r.status_code, r.json())
    assert r.status_code == 200
    # Delete draw
    r = client.delete(f"/api/draws/{ids['draw_id']}")
    print("Delete Draw Response:", r.status_code, r.json())
    assert r.status_code == 200
    # Delete project
    r = client.delete(f"/api/projects/{ids['project_id']}")
    print("Delete Project Response:", r.status_code, r.json())
    assert r.status_code == 200
