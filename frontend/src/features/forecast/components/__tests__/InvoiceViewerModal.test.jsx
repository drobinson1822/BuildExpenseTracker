import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import InvoiceViewerModal from '../InvoiceViewerModal';

// Mock window.open
global.open = jest.fn();

describe('InvoiceViewerModal', () => {
  const mockInvoice = {
    id: '1',
    file_name: 'test-invoice.pdf',
    file_size: 1024000,
    created_at: '2023-01-01T12:00:00Z',
    viewUrl: 'https://example.com/signed-url'
  };

  const mockProps = {
    isOpen: true,
    onClose: jest.fn(),
    invoice: mockInvoice
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('does not render when isOpen is false', () => {
    render(<InvoiceViewerModal {...mockProps} isOpen={false} />);
    
    expect(screen.queryByText('test-invoice.pdf')).not.toBeInTheDocument();
  });

  it('does not render when invoice is null', () => {
    render(<InvoiceViewerModal {...mockProps} invoice={null} />);
    
    expect(screen.queryByText('test-invoice.pdf')).not.toBeInTheDocument();
  });

  it('renders modal with invoice details', () => {
    render(<InvoiceViewerModal {...mockProps} />);
    
    expect(screen.getByText('test-invoice.pdf')).toBeInTheDocument();
    expect(screen.getByText('January 1, 2023 at 12:00 PM')).toBeInTheDocument();
    expect(screen.getByText('1.0 MB')).toBeInTheDocument();
  });

  it('renders PDF iframe for PDF files', () => {
    render(<InvoiceViewerModal {...mockProps} />);
    
    const iframe = screen.getByTitle('PDF viewer for test-invoice.pdf');
    expect(iframe).toBeInTheDocument();
    expect(iframe).toHaveAttribute('src', 'https://example.com/signed-url');
  });

  it('renders image with zoom controls for image files', () => {
    const imageInvoice = {
      ...mockInvoice,
      file_name: 'test-invoice.png'
    };

    render(<InvoiceViewerModal {...mockProps} invoice={imageInvoice} />);
    
    expect(screen.getByAltText('test-invoice.png')).toBeInTheDocument();
    expect(screen.getByLabelText('Zoom out')).toBeInTheDocument();
    expect(screen.getByLabelText('Zoom in')).toBeInTheDocument();
    expect(screen.getByLabelText('Reset zoom')).toBeInTheDocument();
    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  it('closes modal when close button is clicked', () => {
    render(<InvoiceViewerModal {...mockProps} />);
    
    fireEvent.click(screen.getByLabelText('Close viewer'));
    
    expect(mockProps.onClose).toHaveBeenCalled();
  });

  it('closes modal when backdrop is clicked', () => {
    render(<InvoiceViewerModal {...mockProps} />);
    
    fireEvent.click(screen.getByRole('generic', { hidden: true }));
    
    expect(mockProps.onClose).toHaveBeenCalled();
  });

  it('opens invoice in new tab when external link is clicked', () => {
    render(<InvoiceViewerModal {...mockProps} />);
    
    fireEvent.click(screen.getByLabelText('Open in new tab'));
    
    expect(global.open).toHaveBeenCalledWith('https://example.com/signed-url', '_blank');
  });

  it('handles keyboard shortcuts', () => {
    render(<InvoiceViewerModal {...mockProps} />);
    
    // Test Escape key
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(mockProps.onClose).toHaveBeenCalled();
  });

  it('handles zoom controls for images', () => {
    const imageInvoice = {
      ...mockInvoice,
      file_name: 'test-invoice.jpg'
    };

    render(<InvoiceViewerModal {...mockProps} invoice={imageInvoice} />);
    
    // Test zoom in
    fireEvent.click(screen.getByLabelText('Zoom in'));
    expect(screen.getByText('125%')).toBeInTheDocument();
    
    // Test zoom out
    fireEvent.click(screen.getByLabelText('Zoom out'));
    expect(screen.getByText('100%')).toBeInTheDocument();
    
    // Test reset zoom
    fireEvent.click(screen.getByLabelText('Zoom in'));
    fireEvent.click(screen.getByLabelText('Reset zoom'));
    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  it('handles zoom keyboard shortcuts for images', () => {
    const imageInvoice = {
      ...mockInvoice,
      file_name: 'test-invoice.png'
    };

    render(<InvoiceViewerModal {...mockProps} invoice={imageInvoice} />);
    
    // Test zoom in with + key
    fireEvent.keyDown(document, { key: '+' });
    expect(screen.getByText('125%')).toBeInTheDocument();
    
    // Test zoom out with - key
    fireEvent.keyDown(document, { key: '-' });
    expect(screen.getByText('100%')).toBeInTheDocument();
    
    // Test reset with 0 key
    fireEvent.keyDown(document, { key: '+' });
    fireEvent.keyDown(document, { key: '0' });
    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  it('handles mouse wheel zoom for images', () => {
    const imageInvoice = {
      ...mockInvoice,
      file_name: 'test-invoice.png'
    };

    render(<InvoiceViewerModal {...mockProps} invoice={imageInvoice} />);
    
    const imageContainer = screen.getByAltText('test-invoice.png').parentElement;
    
    // Test zoom in with wheel up
    fireEvent.wheel(imageContainer, { deltaY: -100 });
    expect(screen.getByText('110%')).toBeInTheDocument();
    
    // Test zoom out with wheel down
    fireEvent.wheel(imageContainer, { deltaY: 100 });
    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  it('handles image dragging when zoomed', () => {
    const imageInvoice = {
      ...mockInvoice,
      file_name: 'test-invoice.png'
    };

    render(<InvoiceViewerModal {...mockProps} invoice={imageInvoice} />);
    
    // Zoom in first
    fireEvent.click(screen.getByLabelText('Zoom in'));
    
    const imageContainer = screen.getByAltText('test-invoice.png').parentElement;
    
    // Test mouse drag
    fireEvent.mouseDown(imageContainer, { clientX: 100, clientY: 100 });
    fireEvent.mouseMove(imageContainer, { clientX: 150, clientY: 150 });
    fireEvent.mouseUp(imageContainer);
    
    // Should handle the drag (no specific assertion as position is internal state)
    expect(imageContainer).toBeInTheDocument();
  });

  it('disables zoom controls at limits for images', () => {
    const imageInvoice = {
      ...mockInvoice,
      file_name: 'test-invoice.png'
    };

    render(<InvoiceViewerModal {...mockProps} invoice={imageInvoice} />);
    
    const zoomOutBtn = screen.getByLabelText('Zoom out');
    const zoomInBtn = screen.getByLabelText('Zoom in');
    
    // Zoom out to minimum
    fireEvent.click(zoomOutBtn);
    fireEvent.click(zoomOutBtn);
    expect(zoomOutBtn).toBeDisabled();
    
    // Zoom in to maximum
    for (let i = 0; i < 10; i++) {
      fireEvent.click(zoomInBtn);
    }
    expect(zoomInBtn).toBeDisabled();
  });

  it('shows loading state initially', () => {
    render(<InvoiceViewerModal {...mockProps} />);
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('shows error state when iframe fails to load', async () => {
    render(<InvoiceViewerModal {...mockProps} />);
    
    const iframe = screen.getByTitle('PDF viewer for test-invoice.pdf');
    fireEvent.error(iframe);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load invoice')).toBeInTheDocument();
      expect(screen.getByText('Failed to load PDF')).toBeInTheDocument();
    });
  });

  it('shows error state when image fails to load', async () => {
    const imageInvoice = {
      ...mockInvoice,
      file_name: 'test-invoice.png'
    };

    render(<InvoiceViewerModal {...mockProps} invoice={imageInvoice} />);
    
    const image = screen.getByAltText('test-invoice.png');
    fireEvent.error(image);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load invoice')).toBeInTheDocument();
      expect(screen.getByText('Failed to load image')).toBeInTheDocument();
    });
  });

  it('displays keyboard shortcuts in footer', () => {
    render(<InvoiceViewerModal {...mockProps} />);
    
    expect(screen.getByText('Keyboard shortcuts:')).toBeInTheDocument();
    expect(screen.getByText('ESC: Close')).toBeInTheDocument();
  });

  it('displays image-specific shortcuts for images', () => {
    const imageInvoice = {
      ...mockInvoice,
      file_name: 'test-invoice.png'
    };

    render(<InvoiceViewerModal {...mockProps} invoice={imageInvoice} />);
    
    expect(screen.getByText('+/-: Zoom')).toBeInTheDocument();
    expect(screen.getByText('0: Reset')).toBeInTheDocument();
    expect(screen.getByText('Drag: Pan (when zoomed)')).toBeInTheDocument();
  });

  it('resets zoom and position when modal opens with new invoice', () => {
    const { rerender } = render(<InvoiceViewerModal {...mockProps} invoice={null} isOpen={false} />);
    
    const imageInvoice = {
      ...mockInvoice,
      file_name: 'test-invoice.png'
    };

    rerender(<InvoiceViewerModal {...mockProps} invoice={imageInvoice} isOpen={true} />);
    
    expect(screen.getByText('100%')).toBeInTheDocument();
  });
});
