# Frontend Architecture Documentation

## 📁 New Scalable Folder Structure

```
src/
├── components/           # Reusable UI components
│   ├── ui/              # Basic UI elements (Button, Input, Table)
│   │   ├── Button.jsx
│   │   ├── Input.jsx
│   │   ├── Table.jsx
│   │   └── index.js
│   └── layout/          # Layout components
│       ├── Header.jsx
│       ├── Layout.jsx
│       └── index.js
├── features/            # Feature-based modules
│   ├── auth/           # Authentication feature
│   │   └── components/
│   │       ├── LoginForm.jsx
│   │       ├── RegisterForm.jsx
│   │       ├── ProtectedRoute.jsx
│   │       └── index.js
│   ├── projects/       # Project management feature
│   │   └── components/
│   │       ├── ProjectCard.jsx
│   │       ├── ProjectForm.jsx
│   │       └── index.js
│   └── forecast/       # Forecast management feature
│       └── components/
│           ├── ForecastTable.jsx
│           └── index.js
├── pages/              # Page components
│   ├── LoginPage.jsx
│   ├── RegisterPage.jsx
│   ├── ProjectsPage.jsx
│   ├── ProjectDetailPage.jsx
│   └── index.js
├── contexts/           # React contexts
│   └── AuthContext.jsx
├── services/           # API services
│   ├── api.js
│   ├── projectService.js
│   ├── forecastService.js
│   ├── expenseService.js
│   └── index.js
├── hooks/              # Custom React hooks
│   ├── useProjects.js
│   └── index.js
├── utils/              # Utility functions
│   ├── formatters.js
│   ├── constants.js
│   └── index.js
├── App.jsx             # Main app component
├── main.jsx            # App entry point
└── index.css           # Global styles
```

## 🏗️ Architecture Principles

### 1. **Feature-Based Organization**
- Each major feature has its own directory under `features/`
- Components, hooks, and services related to a feature are co-located
- Easy to add new features without cluttering the root

### 2. **Separation of Concerns**
- **Components**: Pure UI components with minimal business logic
- **Services**: API calls and data fetching logic
- **Hooks**: Reusable state management and side effects
- **Utils**: Pure utility functions and constants

### 3. **Reusable UI Components**
- Base UI components in `components/ui/`
- Consistent design system across the app
- Easy to maintain and update styling

### 4. **Service Layer**
- Centralized API communication
- Consistent error handling
- Easy to mock for testing

## 🔧 Key Improvements

### Before (Flat Structure Issues):
- All components in root `src/` directory
- Mixed concerns (UI + business logic)
- Hard to locate related files
- Difficult to scale with new features

### After (Scalable Structure Benefits):
- ✅ **Feature-based organization** - Related code is co-located
- ✅ **Clear separation of concerns** - UI, business logic, and data are separated
- ✅ **Reusable components** - Consistent UI elements across the app
- ✅ **Service layer** - Centralized API management
- ✅ **Custom hooks** - Reusable state management
- ✅ **Easy testing** - Each layer can be tested independently
- ✅ **Scalable** - Easy to add new features without restructuring

## 📋 Migration Status

### ✅ Completed:
- Created new folder structure
- Refactored all existing components
- Updated imports in App.jsx
- Created reusable UI components (Button, Input, Table)
- Implemented service layer for API calls
- Added utility functions and constants
- Created custom hooks for state management

### 🔄 Next Steps for Full Migration:
1. Update any remaining old import paths
2. Test all functionality works with new structure
3. Add more reusable UI components as needed
4. Implement error boundaries
5. Add loading states and error handling components

## 🚀 Future Scalability

This structure supports:
- **New Features**: Add to `features/` directory
- **Shared Components**: Add to `components/ui/`
- **Business Logic**: Add custom hooks in `hooks/`
- **API Integration**: Add services in `services/`
- **Utilities**: Add to `utils/`

## 📖 Usage Examples

### Adding a New Feature:
```
src/features/expenses/
├── components/
│   ├── ExpenseForm.jsx
│   ├── ExpenseList.jsx
│   └── index.js
├── hooks/
│   └── useExpenses.js
└── services/
    └── expenseService.js
```

### Using Reusable Components:
```jsx
import { Button, Input, Table } from '../../../components/ui';

// Consistent styling and behavior across the app
<Button variant="primary" onClick={handleClick}>
  Save Project
</Button>
```

### Service Layer Usage:
```jsx
import { projectService } from '../services';

// Centralized API calls with error handling
const projects = await projectService.getProjects();
```
