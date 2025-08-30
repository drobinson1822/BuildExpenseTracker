import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import Table from '../Table'

describe('Table', () => {
  it('renders basic table structure', () => {
    render(
      <Table>
        <Table.Header>
          <Table.Row>
            <Table.Head>Name</Table.Head>
            <Table.Head>Email</Table.Head>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          <Table.Row>
            <Table.Cell>John Doe</Table.Cell>
            <Table.Cell>john@example.com</Table.Cell>
          </Table.Row>
        </Table.Body>
      </Table>
    )

    expect(screen.getByRole('table')).toBeInTheDocument()
    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Email')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('john@example.com')).toBeInTheDocument()
  })

  it('applies correct CSS classes', () => {
    render(
      <Table>
        <Table.Header>
          <Table.Row>
            <Table.Head>Header</Table.Head>
          </Table.Row>
        </Table.Header>
      </Table>
    )

    const table = screen.getByRole('table')
    expect(table).toHaveClass('min-w-full', 'border', 'bg-white', 'text-sm', 'rounded-xl', 'shadow-sm')
    
    const header = table.querySelector('thead')
    expect(header).toHaveClass('bg-gray-100', 'text-gray-700')
  })

  it('handles clickable rows', () => {
    const handleClick = vi.fn()
    render(
      <Table>
        <Table.Body>
          <Table.Row onClick={handleClick}>
            <Table.Cell>Clickable</Table.Cell>
          </Table.Row>
        </Table.Body>
      </Table>
    )

    const row = screen.getByRole('row')
    expect(row).toHaveClass('cursor-pointer')
    
    fireEvent.click(row)
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('applies custom className to table', () => {
    render(<Table className="custom-table">Content</Table>)
    expect(screen.getByRole('table')).toHaveClass('custom-table')
  })

  it('applies custom className to components', () => {
    render(
      <Table>
        <Table.Header className="custom-header">
          <Table.Row className="custom-row">
            <Table.Head className="custom-head">Header</Table.Head>
          </Table.Row>
        </Table.Header>
        <Table.Body className="custom-body">
          <Table.Row>
            <Table.Cell className="custom-cell">Cell</Table.Cell>
          </Table.Row>
        </Table.Body>
      </Table>
    )

    expect(screen.getByRole('table').querySelector('thead')).toHaveClass('custom-header')
    expect(screen.getByRole('table').querySelector('tbody')).toHaveClass('custom-body')
    expect(screen.getByRole('columnheader')).toHaveClass('custom-head')
    expect(screen.getByRole('cell')).toHaveClass('custom-cell')
  })
})
