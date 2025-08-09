
# 🧠 Feature Prompt: Add “New Project” Functionality (SQLite, Existing DB)

You’re working in an existing codebase using:

- **FastAPI** backend with **SQLAlchemy**, already configured with **SQLite**
- **React + Tailwind** frontend
- The database is already initialized and migrations are being tracked (or models exist)

---

## ✅ TASK: Add "New Project" Functionality

Implement the ability to **create a new project** in the system. This includes:

---

## 1. ✅ Backend Updates

### 📦 Requirements:
- Use the existing database (SQLite, already configured with SQLAlchemy)
- Add a new `POST /projects` endpoint to create a project
- The table `Project` already exists or can be extended with the following fields:

```python
class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    address = Column(String)
    project_type = Column(String)  # Enum (Spec, Custom, Investment)
    sqft_heated = Column(Integer)
    sqft_total = Column(Integer)
    start_date = Column(Date)
    completion_target_date = Column(Date)
    estimated_budget = Column(Numeric)
    target_sales_price = Column(Numeric)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
```

If any of these fields already exist, reuse them. Only add missing ones.

### 🔧 Pydantic Schema:

```python
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str]
    address: Optional[str]
    project_type: Optional[str]
    sqft_heated: Optional[int]
    sqft_total: Optional[int]
    start_date: Optional[date]
    completion_target_date: Optional[date]
    estimated_budget: Optional[float]
    target_sales_price: Optional[float]
    notes: Optional[str]
```

### 🔧 Endpoint:

```python
@router.post("/projects", response_model=ProjectRead)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project
```

---

## 2. ✅ Frontend Updates (React + Tailwind)

### 📄 Create a New Project Page (e.g., `/new-project`)

Build a form with the following fields:
- Project Name (required)
- Description
- Address
- Project Type (dropdown: Spec, Custom, Investment)
- Heated SQFT
- Total SQFT
- Estimated Start Date
- Target Completion Date
- Estimated Budget
- Target Sales Price
- Notes

### 📩 On Submit:
- Make a `POST` request to `/api/projects`
- Redirect to the project dashboard or list on success

---

## ✅ Success Criteria

- Project is added to the database
- Required fields are validated
- Frontend redirects or confirms success
- Form is clean and visually usable (Tailwind layout)
