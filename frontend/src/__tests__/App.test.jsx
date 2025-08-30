import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import App from '../App'

// Mock all the page components
vi.mock('../pages', () => ({
  LoginPage: () => <div>Login Page</div>,
  RegisterPage: () => <div>Register Page</div>,
  ProjectsPage: () => <div>Projects Page</div>,
  ProjectDetailPage: () => <div>Project Detail Page</div>
}))

// Mock auth context
const mockAuthContext = {
  user: null,
  loading: false
}

vi.mock('../contexts/AuthContext', () => ({
  AuthProvider: ({ children }) => children,
  useAuth: () => mockAuthContext
}))

// Mock protected route
vi.mock('../features/auth/components', () => ({
  ProtectedRoute: ({ children }) => children
}))

// Mock layout
vi.mock('../components/layout', () => ({
  Layout: ({ children }) => <div data-testid="layout">{children}</div>
}))

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    // Should render without throwing
  })

  it('renders login page on /login route', () => {
    // Mock window.location
    delete window.location
    window.location = { pathname: '/login' }
    
    render(<App />)
    expect(screen.getByText('Login Page')).toBeInTheDocument()
  })
})
