import { api } from './api';

class InvoiceService {
  /**
   * Get all invoices for a line item
   */
  async getInvoices(lineItemId) {
    try {
      const response = await api.get(`/line-items/${lineItemId}/invoices`);
      return response;
    } catch (error) {
      console.error('Error fetching invoices:', error);
      throw error;
    }
  }

  /**
   * Begin invoice upload process
   */
  async beginUpload(lineItemId, fileData) {
    try {
      const uploadData = {
        line_item_id: lineItemId,
        file_name: fileData.name,
        mime_type: fileData.type,
        file_size: fileData.size
      };

      const response = await api.post(`/line-items/${lineItemId}/invoices:begin-upload`, uploadData);

      return response;
    } catch (error) {
      console.error('Error beginning upload:', error);
      throw error;
    }
  }

  /**
   * Upload file to signed URL
   */
  async uploadFile(signedUrl, file) {
    try {
      const response = await fetch(signedUrl, {
        method: 'PUT',
        body: file,
        headers: {
          'Content-Type': file.type
        }
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      return response;
    } catch (error) {
      console.error('Error uploading file:', error);
      throw error;
    }
  }

  /**
   * Complete invoice upload process
   */
  async completeUpload(lineItemId, invoiceId) {
    try {
      const response = await api.post(`/line-items/${lineItemId}/invoices/${invoiceId}:complete`);

      return response;
    } catch (error) {
      console.error('Error completing upload:', error);
      throw error;
    }
  }

  /**
   * Get signed URL for viewing invoice
   */
  async getViewUrl(lineItemId, invoiceId) {
    try {
      const response = await api.get(`/line-items/${lineItemId}/invoices/${invoiceId}:view-url`);
      return response;
    } catch (error) {
      console.error('Error getting view URL:', error);
      throw error;
    }
  }

  /**
   * Delete an invoice
   */
  async deleteInvoice(lineItemId, invoiceId) {
    try {
      const response = await api.delete(`/line-items/${lineItemId}/invoices/${invoiceId}`);

      return response;
    } catch (error) {
      console.error('Error deleting invoice:', error);
      throw error;
    }
  }

  /**
   * Upload invoice with full two-phase flow
   */
  async uploadInvoice(lineItemId, file) {
    try {
      // Validate file
      this.validateFile(file);

      // Begin upload
      const uploadSessionResponse = await this.beginUpload(lineItemId, file);
      const uploadSession = uploadSessionResponse.data;
      
      // Upload to storage
      await this.uploadFile(uploadSession.upload_url, file);
      
      // Complete upload
      const completedInvoiceResponse = await this.completeUpload(lineItemId, uploadSession.invoice_id);
      
      return completedInvoiceResponse;
    } catch (error) {
      console.error('Error in full upload process:', error);
      throw error;
    }
  }

  /**
   * Validate file before upload
   */
  validateFile(file) {
    const allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!allowedTypes.includes(file.type)) {
      throw new Error(`File type ${file.type} not allowed. Please use PDF, PNG, or JPG files.`);
    }

    if (file.size > maxSize) {
      throw new Error(`File size ${(file.size / 1024 / 1024).toFixed(1)}MB exceeds maximum of 10MB.`);
    }
  }
}

export const invoiceService = new InvoiceService();
