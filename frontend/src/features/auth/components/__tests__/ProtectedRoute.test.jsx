import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import ProtectedRoute from '../ProtectedRoute'

const mockAuthContext = {
  user: null,
  loading: false
}

vi.mock('../../../../contexts/AuthContext', () => ({
  useAuth: () => mockAuthContext
}))

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('ProtectedRoute', () => {
  it('shows loading spinner when loading', () => {
    mockAuthContext.loading = true
    mockAuthContext.user = null
    
    renderWithRouter(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>
    )
    
    expect(screen.getByRole('status', { hidden: true })).toBeInTheDocument() // Loading spinner
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
  })

  it('redirects to login when user is not authenticated', () => {
    mockAuthContext.loading = false
    mockAuthContext.user = null
    
    renderWithRouter(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>
    )
    
    // Should redirect to login, so protected content should not be visible
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
  })

  it('renders children when user is authenticated', () => {
    mockAuthContext.loading = false
    mockAuthContext.user = { id: 1, email: 'test@example.com' }
    
    renderWithRouter(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>
    )
    
    expect(screen.getByText('Protected Content')).toBeInTheDocument()
  })
})
