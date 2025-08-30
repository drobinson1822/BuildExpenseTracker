import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import ForecastTable from '../ForecastTable'

const mockItems = [
  {
    id: 1,
    category: 'Foundation',
    estimated_cost: 10000,
    notes: 'Concrete foundation',
    progress_percent: 50,
    status: 'In Progress',
    start_date: '2024-01-01',
    end_date: '2024-02-01'
  },
  {
    id: 2,
    category: 'Framing',
    estimated_cost: 15000,
    notes: 'Wood framing',
    progress_percent: 0,
    status: 'Not Started',
    start_date: null,
    end_date: null
  }
]

const mockExpenses = [
  {
    id: 1,
    forecast_line_item_id: 1,
    amount_spent: 5000
  }
]

describe('ForecastTable', () => {
  const mockOnAdd = vi.fn()
  const mockOnEdit = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders forecast items correctly', () => {
    render(
      <ForecastTable 
        items={mockItems} 
        expenses={mockExpenses} 
        onAdd={mockOnAdd} 
        onEdit={mockOnEdit} 
      />
    )

    expect(screen.getByText('Foundation')).toBeInTheDocument()
    expect(screen.getByText('Concrete foundation')).toBeInTheDocument()
    expect(screen.getByText('$10000')).toBeInTheDocument()
    expect(screen.getByText('50%')).toBeInTheDocument()
    expect(screen.getByText('In Progress')).toBeInTheDocument()
    
    expect(screen.getByText('Framing')).toBeInTheDocument()
    expect(screen.getByText('Wood framing')).toBeInTheDocument()
    expect(screen.getByText('$15000')).toBeInTheDocument()
    expect(screen.getByText('0%')).toBeInTheDocument()
    expect(screen.getByText('Not Started')).toBeInTheDocument()
  })

  it('calculates actual expenses correctly', () => {
    render(
      <ForecastTable 
        items={mockItems} 
        expenses={mockExpenses} 
        onAdd={mockOnAdd} 
        onEdit={mockOnEdit} 
      />
    )

    // Should show $5000 for item 1 (has expense)
    expect(screen.getByText('$5000')).toBeInTheDocument()
    // Should show $0 for item 2 (no expenses)
    expect(screen.getByText('$0')).toBeInTheDocument()
  })

  it('handles null dates correctly', () => {
    render(
      <ForecastTable 
        items={mockItems} 
        expenses={mockExpenses} 
        onAdd={mockOnAdd} 
        onEdit={mockOnEdit} 
      />
    )

    expect(screen.getAllByText('N/A')).toHaveLength(2) // Two null dates for second item
  })

  it('shows add line item button', () => {
    render(
      <ForecastTable 
        items={mockItems} 
        expenses={mockExpenses} 
        onAdd={mockOnAdd} 
        onEdit={mockOnEdit} 
      />
    )

    expect(screen.getByText('Add Line Item')).toBeInTheDocument()
  })

  it('opens add form when add button is clicked', () => {
    render(
      <ForecastTable 
        items={mockItems} 
        expenses={mockExpenses} 
        onAdd={mockOnAdd} 
        onEdit={mockOnEdit} 
      />
    )

    fireEvent.click(screen.getByText('Add Line Item'))
    
    // Should show input fields for new item
    expect(screen.getByPlaceholderText('Category')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Description')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('0.00')).toBeInTheDocument()
  })

  it('calls onAdd when new item is submitted', async () => {
    render(
      <ForecastTable 
        items={mockItems} 
        expenses={mockExpenses} 
        onAdd={mockOnAdd} 
        onEdit={mockOnEdit} 
      />
    )

    // Open add form
    fireEvent.click(screen.getByText('Add Line Item'))
    
    // Change status
    fireEvent.change(screen.getByTestId('new-status-select'), {
      target: { value: 'In Progress' }
    })
    fireEvent.change(screen.getByTestId('new-description-input'), { 
      target: { value: 'Shingle roof' } 
    })
    fireEvent.change(screen.getByTestId('new-estimated-cost-input'), { 
      target: { value: '8000' } 
    })
    
    // Submit form
    fireEvent.click(screen.getByTitle('Add'))
    
    await waitFor(() => {
      expect(mockOnAdd).toHaveBeenCalledWith(expect.objectContaining({
        category: expect.any(String),
        notes: 'Shingle roof',
        estimated_cost: '8000',
        status: 'In Progress'
      }))
    })
  })

  it('enters edit mode when row is clicked', () => {
    render(
      <ForecastTable 
        items={mockItems} 
        expenses={mockExpenses} 
        onAdd={mockOnAdd} 
        onEdit={mockOnEdit} 
      />
    )

    // Click on first row
    const firstRow = screen.getByText('Foundation').closest('tr')
    fireEvent.click(firstRow)
    
    // Should show input fields for editing
    expect(screen.getByDisplayValue('Foundation')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Concrete foundation')).toBeInTheDocument()
    expect(screen.getByDisplayValue('10000')).toBeInTheDocument()
  })

  it('calls onEdit when edit is saved', async () => {
    mockOnEdit.mockResolvedValueOnce({})
    render(
      <ForecastTable 
        items={mockItems} 
        expenses={mockExpenses} 
        onAdd={mockOnAdd} 
        onEdit={mockOnEdit} 
      />
    )

    // Enter edit mode
    const firstRow = screen.getByText('Foundation').closest('tr')
    fireEvent.click(firstRow)
    
    // Fill in actual cost - this will be in edit mode, so look for the input with the current value
    const actualInput = screen.getByDisplayValue('0')
    fireEvent.change(actualInput, {
      target: { value: '7500' }
    })
    
    // Modify a field
    const categoryInput = screen.getByDisplayValue('Foundation')
    fireEvent.change(categoryInput, { target: { value: 'Updated Foundation' } })
    
    // Save changes
    fireEvent.click(screen.getByTitle('Save'))
    
    await waitFor(() => {
      expect(mockOnEdit).toHaveBeenCalledWith(1, expect.objectContaining({
        category: 'Updated Foundation'
      }))
    })
  })

  it('cancels edit mode when cancel is clicked', () => {
    render(
      <ForecastTable 
        items={mockItems} 
        expenses={mockExpenses} 
        onAdd={mockOnAdd} 
        onEdit={mockOnEdit} 
      />
    )

    // Enter edit mode
    const firstRow = screen.getByText('Foundation').closest('tr')
    fireEvent.click(firstRow)
    
    // Should show edit inputs
    expect(screen.getByDisplayValue('Foundation')).toBeInTheDocument()
    
    // Cancel edit
    fireEvent.click(screen.getByTitle('Cancel'))
    
    // Should return to display mode
    expect(screen.queryByDisplayValue('Foundation')).not.toBeInTheDocument()
    expect(screen.getByText('Foundation')).toBeInTheDocument()
  })

  it('disables add button when adding', () => {
    render(
      <ForecastTable 
        items={mockItems} 
        expenses={mockExpenses} 
        onAdd={mockOnAdd} 
        onEdit={mockOnEdit} 
      />
    )

    // Open add form
    fireEvent.click(screen.getByText('Add Line Item'))
    
    // Add button should be disabled
    expect(screen.getByText('Add Line Item')).toBeDisabled()
  })
})
