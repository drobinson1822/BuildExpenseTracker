import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import Input from '../Input'

describe('Input', () => {
  it('renders basic input', () => {
    render(<Input placeholder="Enter text" />)
    const input = screen.getByPlaceholderText('Enter text')
    
    expect(input).toBeInTheDocument()
    expect(input).toHaveClass('w-full', 'px-3', 'py-2', 'border', 'rounded-lg')
  })

  it('renders with label', () => {
    render(<Input label="Email" />)
    
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
    expect(screen.getByText('Email')).toBeInTheDocument()
  })

  it('renders required indicator', () => {
    render(<Input label="Email" required />)
    
    expect(screen.getByText('*')).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toHaveAttribute('required')
  })

  it('handles value and onChange', () => {
    const handleChange = vi.fn()
    render(<Input value="test" onChange={handleChange} />)
    
    const input = screen.getByDisplayValue('test')
    fireEvent.change(input, { target: { value: 'new value' } })
    
    expect(handleChange).toHaveBeenCalledWith(expect.objectContaining({
      target: expect.objectContaining({ value: 'new value' })
    }))
  })

  it('displays error message', () => {
    render(<Input label="Email" error="Invalid email" />)
    
    expect(screen.getByText('Invalid email')).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toHaveClass('border-red-500')
  })

  it('handles disabled state', () => {
    render(<Input disabled />)
    const input = screen.getByRole('textbox')
    
    expect(input).toBeDisabled()
    expect(input).toHaveClass('bg-gray-100', 'cursor-not-allowed')
  })

  it('renders different input types', () => {
    const { rerender } = render(<Input type="email" />)
    expect(screen.getByRole('textbox')).toHaveAttribute('type', 'email')

    rerender(<Input type="password" />)
    expect(screen.getByLabelText(/password/i)).toHaveAttribute('type', 'password')

    rerender(<Input type="number" />)
    expect(screen.getByRole('spinbutton')).toHaveAttribute('type', 'number')
  })

  it('applies custom className', () => {
    render(<Input className="custom-input" />)
    expect(screen.getByRole('textbox')).toHaveClass('custom-input')
  })
})
