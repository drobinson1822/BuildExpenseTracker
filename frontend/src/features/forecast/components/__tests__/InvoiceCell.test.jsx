import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import InvoiceCell from '../InvoiceCell';
import { invoiceService } from '../../../../services/invoiceService';

// Mock the invoice service
jest.mock('../../../../services/invoiceService');

describe('InvoiceCell', () => {
  const mockOnOpenDrawer = jest.fn();
  const mockLineItemId = 'test-line-item-123';

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('shows loading spinner initially', () => {
    invoiceService.getInvoices.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    render(<InvoiceCell lineItemId={mockLineItemId} onOpenDrawer={mockOnOpenDrawer} />);
    
    expect(screen.getByRole('generic')).toHaveClass('animate-spin');
  });

  it('shows "Add Invoice" button when no invoices exist', async () => {
    invoiceService.getInvoices.mockResolvedValue({ invoices: [] });
    
    render(<InvoiceCell lineItemId={mockLineItemId} onOpenDrawer={mockOnOpenDrawer} />);
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Add invoice' })).toBeInTheDocument();
    });
  });

  it('shows invoice count badge when invoices exist', async () => {
    const mockInvoices = [
      { id: '1', file_name: 'invoice1.pdf' },
      { id: '2', file_name: 'invoice2.pdf' },
      { id: '3', file_name: 'invoice3.pdf' }
    ];
    
    invoiceService.getInvoices.mockResolvedValue({ invoices: mockInvoices });
    
    render(<InvoiceCell lineItemId={mockLineItemId} onOpenDrawer={mockOnOpenDrawer} />);
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: '3 invoices - click to view' })).toBeInTheDocument();
      expect(screen.getByText('3')).toBeInTheDocument();
    });
  });

  it('shows singular label for single invoice', async () => {
    const mockInvoices = [{ id: '1', file_name: 'invoice1.pdf' }];
    
    invoiceService.getInvoices.mockResolvedValue({ invoices: mockInvoices });
    
    render(<InvoiceCell lineItemId={mockLineItemId} onOpenDrawer={mockOnOpenDrawer} />);
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: '1 invoice - click to view' })).toBeInTheDocument();
    });
  });

  it('shows error state when loading fails', async () => {
    invoiceService.getInvoices.mockRejectedValue(new Error('Network error'));
    
    render(<InvoiceCell lineItemId={mockLineItemId} onOpenDrawer={mockOnOpenDrawer} />);
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Error loading invoices - click to retry' })).toBeInTheDocument();
      expect(screen.getByText('Error')).toBeInTheDocument();
    });
  });

  it('calls onOpenDrawer when clicked', async () => {
    const mockInvoices = [{ id: '1', file_name: 'invoice1.pdf' }];
    invoiceService.getInvoices.mockResolvedValue({ invoices: mockInvoices });
    
    render(<InvoiceCell lineItemId={mockLineItemId} onOpenDrawer={mockOnOpenDrawer} />);
    
    await waitFor(() => {
      expect(screen.getByRole('button')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByRole('button'));
    
    expect(mockOnOpenDrawer).toHaveBeenCalledWith(mockLineItemId, mockInvoices);
  });

  it('does not fetch invoices when lineItemId is not provided', () => {
    render(<InvoiceCell lineItemId={null} onOpenDrawer={mockOnOpenDrawer} />);
    
    expect(invoiceService.getInvoices).not.toHaveBeenCalled();
  });

  it('refetches invoices when lineItemId changes', async () => {
    const { rerender } = render(<InvoiceCell lineItemId="item-1" onOpenDrawer={mockOnOpenDrawer} />);
    
    expect(invoiceService.getInvoices).toHaveBeenCalledWith("item-1");
    
    rerender(<InvoiceCell lineItemId="item-2" onOpenDrawer={mockOnOpenDrawer} />);
    
    expect(invoiceService.getInvoices).toHaveBeenCalledWith("item-2");
    expect(invoiceService.getInvoices).toHaveBeenCalledTimes(2);
  });
});
