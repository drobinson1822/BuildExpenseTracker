import { invoiceService } from '../invoiceService';
import { apiService } from '../api';

// Mock the API service
jest.mock('../api');

// Mock fetch for direct storage uploads
global.fetch = jest.fn();

describe('InvoiceService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getInvoices', () => {
    it('fetches invoices for a line item', async () => {
      const mockResponse = {
        invoices: [
          { id: '1', file_name: 'invoice1.pdf' },
          { id: '2', file_name: 'invoice2.pdf' }
        ]
      };
      
      apiService.request.mockResolvedValue(mockResponse);
      
      const result = await invoiceService.getInvoices('line-item-123');
      
      expect(apiService.request).toHaveBeenCalledWith('/api/line-items/line-item-123/invoices');
      expect(result).toEqual(mockResponse);
    });

    it('handles errors when fetching invoices', async () => {
      const error = new Error('Network error');
      apiService.request.mockRejectedValue(error);
      
      await expect(invoiceService.getInvoices('line-item-123')).rejects.toThrow('Network error');
    });
  });

  describe('beginUpload', () => {
    it('begins upload process with file metadata', async () => {
      const mockFile = {
        name: 'test.pdf',
        type: 'application/pdf',
        size: 1024
      };
      
      const mockResponse = {
        invoice_id: 'invoice-123',
        upload_url: 'https://storage.example.com/signed-url'
      };
      
      apiService.request.mockResolvedValue(mockResponse);
      
      const result = await invoiceService.beginUpload('line-item-123', mockFile);
      
      expect(apiService.request).toHaveBeenCalledWith('/api/line-items/line-item-123/invoices:begin-upload', {
        method: 'POST',
        body: {
          line_item_id: 'line-item-123',
          file_name: 'test.pdf',
          mime_type: 'application/pdf',
          file_size: 1024
        }
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('uploadFile', () => {
    it('uploads file to signed URL', async () => {
      const mockFile = new File(['content'], 'test.pdf', { type: 'application/pdf' });
      const signedUrl = 'https://storage.example.com/signed-url';
      
      fetch.mockResolvedValue({ ok: true });
      
      await invoiceService.uploadFile(signedUrl, mockFile);
      
      expect(fetch).toHaveBeenCalledWith(signedUrl, {
        method: 'PUT',
        body: mockFile,
        headers: {
          'Content-Type': 'application/pdf'
        }
      });
    });

    it('throws error when upload fails', async () => {
      const mockFile = new File(['content'], 'test.pdf', { type: 'application/pdf' });
      const signedUrl = 'https://storage.example.com/signed-url';
      
      fetch.mockResolvedValue({ ok: false, statusText: 'Forbidden' });
      
      await expect(invoiceService.uploadFile(signedUrl, mockFile)).rejects.toThrow('Upload failed: Forbidden');
    });
  });

  describe('completeUpload', () => {
    it('completes upload process', async () => {
      const mockResponse = {
        id: 'invoice-123',
        file_name: 'test.pdf',
        status: 'uploaded'
      };
      
      apiService.request.mockResolvedValue(mockResponse);
      
      const result = await invoiceService.completeUpload('line-item-123', 'invoice-123');
      
      expect(apiService.request).toHaveBeenCalledWith('/api/line-items/line-item-123/invoices/invoice-123:complete', {
        method: 'POST'
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getViewUrl', () => {
    it('gets signed URL for viewing invoice', async () => {
      const mockResponse = {
        view_url: 'https://storage.example.com/view-url'
      };
      
      apiService.request.mockResolvedValue(mockResponse);
      
      const result = await invoiceService.getViewUrl('line-item-123', 'invoice-123');
      
      expect(apiService.request).toHaveBeenCalledWith('/api/line-items/line-item-123/invoices/invoice-123:view-url');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('deleteInvoice', () => {
    it('deletes an invoice', async () => {
      apiService.request.mockResolvedValue({});
      
      await invoiceService.deleteInvoice('line-item-123', 'invoice-123');
      
      expect(apiService.request).toHaveBeenCalledWith('/api/line-items/line-item-123/invoices/invoice-123', {
        method: 'DELETE'
      });
    });
  });

  describe('uploadInvoice', () => {
    it('performs complete upload flow', async () => {
      const mockFile = new File(['content'], 'test.pdf', { type: 'application/pdf', size: 1024 });
      
      const beginResponse = {
        invoice_id: 'invoice-123',
        upload_url: 'https://storage.example.com/signed-url'
      };
      
      const completeResponse = {
        id: 'invoice-123',
        file_name: 'test.pdf',
        status: 'uploaded'
      };
      
      apiService.request
        .mockResolvedValueOnce(beginResponse)
        .mockResolvedValueOnce(completeResponse);
      
      fetch.mockResolvedValue({ ok: true });
      
      const result = await invoiceService.uploadInvoice('line-item-123', mockFile);
      
      expect(apiService.request).toHaveBeenCalledTimes(2);
      expect(fetch).toHaveBeenCalledWith('https://storage.example.com/signed-url', expect.any(Object));
      expect(result).toEqual(completeResponse);
    });

    it('validates file before upload', async () => {
      const invalidFile = new File(['content'], 'test.txt', { type: 'text/plain' });
      
      await expect(invoiceService.uploadInvoice('line-item-123', invalidFile)).rejects.toThrow('File type text/plain not allowed');
    });
  });

  describe('validateFile', () => {
    it('accepts valid PDF files', () => {
      const validFile = new File(['content'], 'test.pdf', { type: 'application/pdf', size: 1024 });
      
      expect(() => invoiceService.validateFile(validFile)).not.toThrow();
    });

    it('accepts valid image files', () => {
      const validFiles = [
        new File(['content'], 'test.png', { type: 'image/png', size: 1024 }),
        new File(['content'], 'test.jpg', { type: 'image/jpeg', size: 1024 }),
        new File(['content'], 'test.jpeg', { type: 'image/jpg', size: 1024 })
      ];
      
      validFiles.forEach(file => {
        expect(() => invoiceService.validateFile(file)).not.toThrow();
      });
    });

    it('rejects invalid file types', () => {
      const invalidFile = new File(['content'], 'test.txt', { type: 'text/plain' });
      
      expect(() => invoiceService.validateFile(invalidFile)).toThrow('File type text/plain not allowed');
    });

    it('rejects files that are too large', () => {
      const largeFile = new File(['content'], 'large.pdf', { type: 'application/pdf' });
      Object.defineProperty(largeFile, 'size', { value: 15 * 1024 * 1024 }); // 15MB
      
      expect(() => invoiceService.validateFile(largeFile)).toThrow('File size 15.0MB exceeds maximum of 10MB');
    });

    it('accepts files at the size limit', () => {
      const maxSizeFile = new File(['content'], 'max.pdf', { type: 'application/pdf' });
      Object.defineProperty(maxSizeFile, 'size', { value: 10 * 1024 * 1024 }); // Exactly 10MB
      
      expect(() => invoiceService.validateFile(maxSizeFile)).not.toThrow();
    });
  });
});
