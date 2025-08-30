import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import userEvent from '@testing-library/user-event'
import App from '../../App'
import { server } from '../../test/mocks/server'

// Start mock server
beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

const renderApp = () => {
  return render(
    <BrowserRouter>
      <App />
    </BrowserRouter>
  )
}

describe('User Flows Integration Tests', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('complete user registration and project creation flow', async () => {
    const user = userEvent.setup()
    
    // Start at login page (assuming redirect)
    renderApp()
    
    // Navigate to register
    const registerLink = screen.getByText(/create a new account/i)
    await user.click(registerLink)
    
    // Fill registration form
    await user.type(screen.getByLabelText(/full name/i), 'John Doe')
    await user.type(screen.getByLabelText(/^email/i), 'john@example.com')
    await user.type(screen.getByLabelText(/^password/i), 'password123')
    await user.type(screen.getByLabelText(/confirm password/i), 'password123')
    
    // Submit registration
    await user.click(screen.getByRole('button', { name: /create account/i }))
    
    // Should redirect to projects page after successful registration
    await waitFor(() => {
      expect(screen.getByText('Projects')).toBeInTheDocument()
    })
    
    // Create new project
    await user.click(screen.getByText('Create New Project'))
    
    // Fill project form
    await user.type(screen.getByLabelText(/project name/i), 'My Test Project')
    await user.type(screen.getByLabelText(/address/i), '123 Test Street')
    
    // Submit project creation
    await user.click(screen.getByText('Create Project'))
    
    // Should see the new project in the list
    await waitFor(() => {
      expect(screen.getByText('My Test Project')).toBeInTheDocument()
    })
  })

  it('login and navigate to project details flow', async () => {
    const user = userEvent.setup()
    
    renderApp()
    
    // Fill login form
    await user.type(screen.getByLabelText(/email/i), 'test@example.com')
    await user.type(screen.getByLabelText(/password/i), 'password123')
    
    // Submit login
    await user.click(screen.getByRole('button', { name: /sign in/i }))
    
    // Should redirect to projects page
    await waitFor(() => {
      expect(screen.getByText('Projects')).toBeInTheDocument()
    })
    
    // Click on project to view details
    const viewDetailsButton = screen.getByText('View Details')
    await user.click(viewDetailsButton)
    
    // Should navigate to project detail page
    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
      expect(screen.getByText('Forecast & Tracking')).toBeInTheDocument()
    })
  })

  it('add forecast item flow', async () => {
    const user = userEvent.setup()
    
    // Mock being logged in and on project detail page
    localStorage.setItem('token', 'mock-token')
    
    renderApp()
    
    // Navigate to project details (assuming we're already logged in)
    await waitFor(() => {
      expect(screen.getByText('Add Line Item')).toBeInTheDocument()
    })
    
    // Click add line item
    await user.click(screen.getByText('Add Line Item'))
    
    // Fill forecast item form
    await user.type(screen.getByPlaceholderText('Category'), 'Foundation Work')
    await user.type(screen.getByPlaceholderText('Description'), 'Concrete foundation and footings')
    await user.type(screen.getByPlaceholderText('0.00'), '15000')
    
    // Submit forecast item
    await user.click(screen.getByTitle('Add'))
    
    // Should see the new forecast item in the table
    await waitFor(() => {
      expect(screen.getByText('Foundation Work')).toBeInTheDocument()
      expect(screen.getByText('Concrete foundation and footings')).toBeInTheDocument()
    })
  })

  it('edit forecast item flow', async () => {
    const user = userEvent.setup()
    
    localStorage.setItem('token', 'mock-token')
    renderApp()
    
    // Wait for forecast table to load
    await waitFor(() => {
      expect(screen.getByText('Foundation')).toBeInTheDocument()
    })
    
    // Click on a forecast item row to edit
    const foundationRow = screen.getByText('Foundation').closest('tr')
    await user.click(foundationRow)
    
    // Should enter edit mode with input fields
    await waitFor(() => {
      expect(screen.getByDisplayValue('Foundation')).toBeInTheDocument()
    })
    
    // Modify the category
    const categoryInput = screen.getByDisplayValue('Foundation')
    await user.clear(categoryInput)
    await user.type(categoryInput, 'Updated Foundation')
    
    // Save changes
    await user.click(screen.getByTitle('Save'))
    
    // Should exit edit mode and show updated value
    await waitFor(() => {
      expect(screen.getByText('Updated Foundation')).toBeInTheDocument()
      expect(screen.queryByDisplayValue('Updated Foundation')).not.toBeInTheDocument()
    })
  })

  it('logout flow', async () => {
    const user = userEvent.setup()
    
    localStorage.setItem('token', 'mock-token')
    renderApp()
    
    // Should be on projects page when logged in
    await waitFor(() => {
      expect(screen.getByText('Projects')).toBeInTheDocument()
    })
    
    // Click logout button
    await user.click(screen.getByText('Logout'))
    
    // Should redirect to login page
    await waitFor(() => {
      expect(screen.getByText(/sign in to your account/i)).toBeInTheDocument()
    })
    
    // Token should be cleared
    expect(localStorage.getItem('token')).toBeNull()
  })
})
