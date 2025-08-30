import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import ProjectCard from '../ProjectCard'

const mockProject = {
  id: 1,
  name: 'Test Project',
  address: '123 Test St',
  status: 'in_progress',
  start_date: '2024-01-01',
  target_completion_date: '2024-12-31',
  total_sqft: 2000
}

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('ProjectCard', () => {
  const mockOnEdit = vi.fn()
  const mockOnDelete = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders project information correctly', () => {
    renderWithRouter(
      <ProjectCard 
        project={mockProject} 
        onEdit={mockOnEdit} 
        onDelete={mockOnDelete} 
      />
    )

    expect(screen.getByText('Test Project')).toBeInTheDocument()
    expect(screen.getByText('123 Test St')).toBeInTheDocument()
    expect(screen.getByText('IN PROGRESS')).toBeInTheDocument()
    expect(screen.getByText('1/1/2024')).toBeInTheDocument()
    expect(screen.getByText('12/31/2024')).toBeInTheDocument()
    expect(screen.getByText('2,000')).toBeInTheDocument()
  })

  it('handles missing optional fields', () => {
    const minimalProject = {
      id: 2,
      name: 'Minimal Project',
      status: null
    }

    renderWithRouter(
      <ProjectCard 
        project={minimalProject} 
        onEdit={mockOnEdit} 
        onDelete={mockOnDelete} 
      />
    )

    expect(screen.getByText('Minimal Project')).toBeInTheDocument()
    expect(screen.getByText('NOT STARTED')).toBeInTheDocument()
    expect(screen.getAllByText('Not set')).toHaveLength(2) // start and end dates
  })

  it('displays correct status colors', () => {
    const { rerender } = renderWithRouter(
      <ProjectCard 
        project={{ ...mockProject, status: 'completed' }} 
        onEdit={mockOnEdit} 
        onDelete={mockOnDelete} 
      />
    )
    expect(screen.getByText('COMPLETED')).toHaveClass('bg-green-100', 'text-green-800')

    rerender(
      <ProjectCard 
        project={{ ...mockProject, status: 'not_started' }} 
        onEdit={mockOnEdit} 
        onDelete={mockOnDelete} 
      />
    )
    expect(screen.getByText('NOT STARTED')).toHaveClass('bg-gray-100', 'text-gray-800')
  })

  it('calls onEdit when edit button is clicked', () => {
    renderWithRouter(
      <ProjectCard 
        project={mockProject} 
        onEdit={mockOnEdit} 
        onDelete={mockOnDelete} 
      />
    )

    fireEvent.click(screen.getByText('Edit'))
    expect(mockOnEdit).toHaveBeenCalledWith(mockProject)
  })

  it('calls onDelete when delete button is clicked', () => {
    renderWithRouter(
      <ProjectCard 
        project={mockProject} 
        onEdit={mockOnEdit} 
        onDelete={mockOnDelete} 
      />
    )

    fireEvent.click(screen.getByText('Delete'))
    expect(mockOnDelete).toHaveBeenCalledWith(mockProject.id)
  })

  it('has correct link to project details', () => {
    renderWithRouter(
      <ProjectCard 
        project={mockProject} 
        onEdit={mockOnEdit} 
        onDelete={mockOnDelete} 
      />
    )

    const viewDetailsLink = screen.getByText('View Details').closest('a')
    expect(viewDetailsLink).toHaveAttribute('href', '/projects/1')
  })
})
