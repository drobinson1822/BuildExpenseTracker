import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import InvoiceDrawer from '../InvoiceDrawer';
import { invoiceService } from '../../../../services/invoiceService';

// Mock the invoice service
jest.mock('../../../../services/invoiceService');

// Mock file for testing
const createMockFile = (name = 'test.pdf', type = 'application/pdf', size = 1024) => {
  const file = new File(['test content'], name, { type });
  Object.defineProperty(file, 'size', { value: size });
  return file;
};

describe('InvoiceDrawer', () => {
  const mockProps = {
    isOpen: true,
    onClose: jest.fn(),
    lineItemId: 'test-line-item-123',
    initialInvoices: [],
    onInvoiceUpdate: jest.fn(),
    onViewInvoice: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
    global.confirm = jest.fn(() => true);
  });

  it('does not render when isOpen is false', () => {
    render(<InvoiceDrawer {...mockProps} isOpen={false} />);
    
    expect(screen.queryByText('Invoice Management')).not.toBeInTheDocument();
  });

  it('renders drawer when isOpen is true', () => {
    render(<InvoiceDrawer {...mockProps} />);
    
    expect(screen.getByText('Invoice Management')).toBeInTheDocument();
    expect(screen.getByText('Drop files here or')).toBeInTheDocument();
  });

  it('shows empty state when no invoices', () => {
    render(<InvoiceDrawer {...mockProps} />);
    
    expect(screen.getByText('No invoices uploaded yet')).toBeInTheDocument();
    expect(screen.getByText('Upload your first invoice above')).toBeInTheDocument();
  });

  it('displays invoice list when invoices exist', () => {
    const mockInvoices = [
      {
        id: '1',
        file_name: 'invoice1.pdf',
        file_size: 1024000,
        created_at: '2023-01-01T00:00:00Z'
      },
      {
        id: '2',
        file_name: 'invoice2.png',
        file_size: 2048000,
        created_at: '2023-01-02T00:00:00Z'
      }
    ];

    render(<InvoiceDrawer {...mockProps} initialInvoices={mockInvoices} />);
    
    expect(screen.getByText('invoice1.pdf')).toBeInTheDocument();
    expect(screen.getByText('invoice2.png')).toBeInTheDocument();
    expect(screen.getByText('1000 KB')).toBeInTheDocument();
    expect(screen.getByText('2000 KB')).toBeInTheDocument();
  });

  it('closes drawer when close button is clicked', () => {
    render(<InvoiceDrawer {...mockProps} />);
    
    fireEvent.click(screen.getByLabelText('Close drawer'));
    
    expect(mockProps.onClose).toHaveBeenCalled();
  });

  it('closes drawer when backdrop is clicked', () => {
    render(<InvoiceDrawer {...mockProps} />);
    
    fireEvent.click(screen.getByRole('generic', { hidden: true }));
    
    expect(mockProps.onClose).toHaveBeenCalled();
  });

  it('handles file upload via file input', async () => {
    const mockFile = createMockFile();
    invoiceService.uploadInvoice.mockResolvedValue({
      id: 'new-invoice',
      file_name: 'test.pdf',
      file_size: 1024,
      created_at: '2023-01-01T00:00:00Z'
    });

    render(<InvoiceDrawer {...mockProps} />);
    
    const fileInput = screen.getByRole('button', { name: /browse/i });
    fireEvent.click(fileInput);
    
    const hiddenInput = document.querySelector('input[type="file"]');
    fireEvent.change(hiddenInput, { target: { files: [mockFile] } });
    
    await waitFor(() => {
      expect(invoiceService.uploadInvoice).toHaveBeenCalledWith('test-line-item-123', mockFile);
    });
  });

  it('handles drag and drop upload', async () => {
    const mockFile = createMockFile();
    invoiceService.uploadInvoice.mockResolvedValue({
      id: 'new-invoice',
      file_name: 'test.pdf',
      file_size: 1024,
      created_at: '2023-01-01T00:00:00Z'
    });

    render(<InvoiceDrawer {...mockProps} />);
    
    const dropZone = screen.getByText('Drop files here or').closest('div');
    
    fireEvent.dragEnter(dropZone);
    fireEvent.dragOver(dropZone);
    fireEvent.drop(dropZone, {
      dataTransfer: {
        files: [mockFile]
      }
    });
    
    await waitFor(() => {
      expect(invoiceService.uploadInvoice).toHaveBeenCalledWith('test-line-item-123', mockFile);
    });
  });

  it('shows upload progress during file upload', async () => {
    const mockFile = createMockFile();
    invoiceService.uploadInvoice.mockImplementation(() => 
      new Promise(resolve => setTimeout(resolve, 1000))
    );

    render(<InvoiceDrawer {...mockProps} />);
    
    const hiddenInput = document.querySelector('input[type="file"]');
    fireEvent.change(hiddenInput, { target: { files: [mockFile] } });
    
    expect(screen.getByText('Uploading...')).toBeInTheDocument();
    expect(screen.getByRole('progressbar', { hidden: true })).toBeInTheDocument();
  });

  it('displays error message on upload failure', async () => {
    const mockFile = createMockFile();
    invoiceService.uploadInvoice.mockRejectedValue(new Error('Upload failed'));

    render(<InvoiceDrawer {...mockProps} />);
    
    const hiddenInput = document.querySelector('input[type="file"]');
    fireEvent.change(hiddenInput, { target: { files: [mockFile] } });
    
    await waitFor(() => {
      expect(screen.getByText('Upload failed')).toBeInTheDocument();
    });
  });

  it('handles invoice deletion', async () => {
    const mockInvoices = [{
      id: '1',
      file_name: 'invoice1.pdf',
      file_size: 1024000,
      created_at: '2023-01-01T00:00:00Z'
    }];

    invoiceService.deleteInvoice.mockResolvedValue();

    render(<InvoiceDrawer {...mockProps} initialInvoices={mockInvoices} />);
    
    fireEvent.click(screen.getByLabelText('Delete invoice1.pdf'));
    
    await waitFor(() => {
      expect(invoiceService.deleteInvoice).toHaveBeenCalledWith('test-line-item-123', '1');
    });
    
    expect(mockProps.onInvoiceUpdate).toHaveBeenCalledWith([]);
  });

  it('handles invoice viewing', async () => {
    const mockInvoices = [{
      id: '1',
      file_name: 'invoice1.pdf',
      file_size: 1024000,
      created_at: '2023-01-01T00:00:00Z'
    }];

    invoiceService.getViewUrl.mockResolvedValue({
      view_url: 'https://example.com/signed-url'
    });

    render(<InvoiceDrawer {...mockProps} initialInvoices={mockInvoices} />);
    
    fireEvent.click(screen.getByLabelText('View invoice1.pdf'));
    
    await waitFor(() => {
      expect(invoiceService.getViewUrl).toHaveBeenCalledWith('test-line-item-123', '1');
    });
    
    expect(mockProps.onViewInvoice).toHaveBeenCalledWith({
      id: '1',
      file_name: 'invoice1.pdf',
      file_size: 1024000,
      created_at: '2023-01-01T00:00:00Z',
      viewUrl: 'https://example.com/signed-url'
    });
  });

  it('validates file types and shows error for invalid files', async () => {
    const invalidFile = createMockFile('test.txt', 'text/plain');
    
    render(<InvoiceDrawer {...mockProps} />);
    
    const hiddenInput = document.querySelector('input[type="file"]');
    fireEvent.change(hiddenInput, { target: { files: [invalidFile] } });
    
    await waitFor(() => {
      expect(screen.getByText(/File type text\/plain not allowed/)).toBeInTheDocument();
    });
  });

  it('validates file size and shows error for large files', async () => {
    const largeFile = createMockFile('large.pdf', 'application/pdf', 15 * 1024 * 1024); // 15MB
    
    render(<InvoiceDrawer {...mockProps} />);
    
    const hiddenInput = document.querySelector('input[type="file"]');
    fireEvent.change(hiddenInput, { target: { files: [largeFile] } });
    
    await waitFor(() => {
      expect(screen.getByText(/File size 15.0MB exceeds maximum of 10MB/)).toBeInTheDocument();
    });
  });

  it('refreshes invoices when drawer opens', async () => {
    invoiceService.getInvoices.mockResolvedValue({ invoices: [] });
    
    const { rerender } = render(<InvoiceDrawer {...mockProps} isOpen={false} />);
    
    expect(invoiceService.getInvoices).not.toHaveBeenCalled();
    
    rerender(<InvoiceDrawer {...mockProps} isOpen={true} />);
    
    expect(invoiceService.getInvoices).toHaveBeenCalledWith('test-line-item-123');
  });
});
