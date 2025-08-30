import React from 'react'
import { render } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from '../contexts/AuthContext'

// Mock auth context for tests
export const createMockAuthContext = (overrides = {}) => ({
  user: null,
  loading: false,
  login: vi.fn(),
  register: vi.fn(),
  logout: vi.fn(),
  ...overrides
})

// Test wrapper with all providers
export const TestWrapper = ({ children, authContext = {} }) => {
  const mockAuthContext = createMockAuthContext(authContext)
  
  return (
    <BrowserRouter>
      <AuthProvider value={mockAuthContext}>
        {children}
      </AuthProvider>
    </BrowserRouter>
  )
}

// Custom render function with providers
export const renderWithProviders = (ui, options = {}) => {
  const { authContext, ...renderOptions } = options
  
  return render(ui, {
    wrapper: ({ children }) => (
      <TestWrapper authContext={authContext}>
        {children}
      </TestWrapper>
    ),
    ...renderOptions
  })
}

// Re-export everything from testing library
export * from '@testing-library/react'
export { renderWithProviders as render }
