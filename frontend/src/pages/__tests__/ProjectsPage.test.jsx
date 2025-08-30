import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import ProjectsPage from '../ProjectsPage'
import { projectService } from '../../services'

// Mock the project service
vi.mock('../../services', () => ({
  projectService: {
    getProjects: vi.fn(),
    createProject: vi.fn(),
    updateProject: vi.fn(),
    deleteProject: vi.fn()
  }
}))

// Mock window.confirm
global.confirm = vi.fn()

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('ProjectsPage', () => {
  const mockProjects = [
    {
      id: 1,
      name: 'Test Project',
      address: '123 Test St',
      status: 'in_progress',
      start_date: '2024-01-01',
      target_completion_date: '2024-12-31',
      total_sqft: 2000
    }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    projectService.getProjects.mockResolvedValue(mockProjects)
  })

  it('renders projects page with project list', async () => {
    renderWithRouter(<ProjectsPage />)

    expect(screen.getByText('Projects')).toBeInTheDocument()
    expect(screen.getByText('Create New Project')).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
    })
  })

  it('shows loading state initially', () => {
    renderWithRouter(<ProjectsPage />)
    
    expect(screen.getByRole('status', { hidden: true })).toBeInTheDocument() // Loading spinner
  })

  it('shows empty state when no projects', async () => {
    projectService.getProjects.mockResolvedValueOnce([])
    renderWithRouter(<ProjectsPage />)

    await waitFor(() => {
      expect(screen.getByText('No projects yet')).toBeInTheDocument()
      expect(screen.getByText('Create your first project to get started')).toBeInTheDocument()
    })
  })

  it('opens create form when create button is clicked', async () => {
    renderWithRouter(<ProjectsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Create New Project'))
    
    expect(screen.getByText('Create New Project')).toBeInTheDocument()
    expect(screen.getByLabelText(/project name/i)).toBeInTheDocument()
  })

  it('creates new project successfully', async () => {
    const newProject = { id: 2, name: 'New Project', status: 'not_started' }
    projectService.createProject.mockResolvedValueOnce(newProject)
    
    renderWithRouter(<ProjectsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
    })

    // Open create form
    fireEvent.click(screen.getByText('Create New Project'))
    
    // Fill form
    fireEvent.change(screen.getByLabelText(/project name/i), {
      target: { value: 'New Project' }
    })
    
    // Submit form
    fireEvent.click(screen.getByText('Create Project'))

    await waitFor(() => {
      expect(projectService.createProject).toHaveBeenCalledWith(
        expect.objectContaining({ name: 'New Project' })
      )
    })
  })

  it('handles project deletion with confirmation', async () => {
    global.confirm.mockReturnValueOnce(true)
    projectService.deleteProject.mockResolvedValueOnce()
    
    renderWithRouter(<ProjectsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
    })

    // Click delete button (assuming it's rendered by ProjectCard)
    const deleteButton = screen.getByText('Delete')
    fireEvent.click(deleteButton)

    expect(global.confirm).toHaveBeenCalledWith('Are you sure you want to delete this project?')
    
    await waitFor(() => {
      expect(projectService.deleteProject).toHaveBeenCalledWith(1)
    })
  })

  it('cancels deletion when user declines confirmation', async () => {
    global.confirm.mockReturnValueOnce(false)
    
    renderWithRouter(<ProjectsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
    })

    const deleteButton = screen.getByText('Delete')
    fireEvent.click(deleteButton)

    expect(global.confirm).toHaveBeenCalled()
    expect(projectService.deleteProject).not.toHaveBeenCalled()
  })

  it('opens edit form when edit button is clicked', async () => {
    renderWithRouter(<ProjectsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Edit'))
    
    expect(screen.getByText('Edit Project')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Test Project')).toBeInTheDocument()
  })

  it('updates project successfully', async () => {
    const updatedProject = { ...mockProjects[0], name: 'Updated Project' }
    projectService.updateProject.mockResolvedValueOnce(updatedProject)
    
    renderWithRouter(<ProjectsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
    })

    // Open edit form
    fireEvent.click(screen.getByText('Edit'))
    
    // Update name
    const nameInput = screen.getByDisplayValue('Test Project')
    fireEvent.change(nameInput, { target: { value: 'Updated Project' } })
    
    // Submit form
    fireEvent.click(screen.getByText('Update Project'))

    await waitFor(() => {
      expect(projectService.updateProject).toHaveBeenCalledWith(
        1,
        expect.objectContaining({ name: 'Updated Project' })
      )
    })
  })

  it('cancels form when cancel button is clicked', async () => {
    renderWithRouter(<ProjectsPage />)

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
    })

    // Open create form
    fireEvent.click(screen.getByText('Create New Project'))
    expect(screen.getByText('Create New Project')).toBeInTheDocument()
    
    // Cancel form
    fireEvent.click(screen.getByText('Cancel'))
    expect(screen.queryByLabelText(/project name/i)).not.toBeInTheDocument()
  })
})
