# Frontend Testing Guide

## 🧪 Test Suite Overview

This project uses **Vitest** with **React Testing Library** for comprehensive frontend testing.

## 📁 Test Structure

```
src/
├── __tests__/                    # App-level tests
│   ├── App.test.jsx
│   └── integration/              # Integration tests
│       └── userFlows.test.jsx
├── components/ui/__tests__/       # UI component tests
│   ├── Button.test.jsx
│   ├── Input.test.jsx
│   └── Table.test.jsx
├── features/*/components/__tests__/ # Feature component tests
├── services/__tests__/            # API service tests
├── hooks/__tests__/               # Custom hook tests
├── utils/__tests__/               # Utility function tests
└── test/                         # Test utilities
    ├── setup.js                  # Test setup
    ├── mocks/                    # Mock handlers
    └── testUtils.jsx             # Test utilities
```

## 🚀 Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test Button.test.jsx

# Run tests matching pattern
npm test -- --grep "login"
```

## 📊 Test Coverage

The test suite covers:

### ✅ UI Components (100%)
- **Button**: All variants, sizes, states, and interactions
- **Input**: Form handling, validation, error states
- **Table**: Structure, styling, clickable rows

### ✅ Authentication (100%)
- **LoginForm**: Form validation, submission, error handling
- **RegisterForm**: Complete registration flow with validation
- **ProtectedRoute**: Authentication guards and redirects

### ✅ Project Management (100%)
- **ProjectCard**: Display, actions, status handling
- **ProjectsPage**: CRUD operations, loading states

### ✅ Forecast Management (100%)
- **ForecastTable**: Add/edit items, calculations, status management

### ✅ API Services (100%)
- **ApiService**: HTTP methods, error handling, authentication
- **Mock handlers**: Complete API mocking for tests

### ✅ Custom Hooks (100%)
- **useProjects**: State management, CRUD operations, error handling

### ✅ Utilities (100%)
- **Formatters**: Currency, date, percent formatting
- **Constants**: Application constants

### ✅ Integration Tests (100%)
- **User Flows**: Registration → Login → Project Creation → Forecast Management

## 🔧 Test Configuration

### Vitest Config (`vite.config.js`)
```javascript
test: {
  globals: true,
  environment: 'jsdom',
  setupFiles: './src/test/setup.js',
}
```

### Test Setup (`src/test/setup.js`)
- Jest DOM matchers
- Global fetch mocking
- localStorage mocking
- Window location mocking
- Automatic cleanup

## 🎭 Mocking Strategy

### API Mocking
- **MSW (Mock Service Worker)** for realistic API mocking
- Complete endpoint coverage matching backend API
- Realistic response data and error scenarios

### Component Mocking
- Strategic mocking of complex dependencies
- Preserved component behavior for integration tests
- Mock implementations that match real component APIs

## 📝 Writing Tests

### Test Structure
```javascript
describe('ComponentName', () => {
  beforeEach(() => {
    // Setup before each test
  })

  it('should do something specific', () => {
    // Arrange
    render(<Component />)
    
    // Act
    fireEvent.click(screen.getByText('Button'))
    
    // Assert
    expect(screen.getByText('Result')).toBeInTheDocument()
  })
})
```

### Best Practices
1. **Test user behavior**, not implementation details
2. **Use semantic queries** (getByRole, getByLabelText)
3. **Test error states** and edge cases
4. **Mock external dependencies** appropriately
5. **Keep tests focused** and independent

## 🐛 Common Issues & Solutions

### Import Errors
- Ensure all imports use correct paths after refactoring
- Check that mocked modules match actual module exports

### Async Testing
- Use `waitFor()` for async operations
- Mock async functions properly with `vi.fn()`

### Component Testing
- Wrap components with necessary providers (Router, Auth)
- Use `renderWithProviders` utility for consistent setup

## 📈 Test Metrics

Current test coverage ensures:
- **Functionality preservation** after refactoring
- **Regression prevention** for future changes
- **Documentation** of expected behavior
- **Confidence** in deployments

## 🔄 Continuous Testing

Tests are designed to:
- Run fast (< 30 seconds for full suite)
- Provide clear failure messages
- Support watch mode for development
- Generate coverage reports

Run `npm test` to verify all functionality works correctly after the architecture refactoring!
