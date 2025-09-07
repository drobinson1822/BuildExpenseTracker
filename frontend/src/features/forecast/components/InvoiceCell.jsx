import React, { useState, useEffect } from 'react';
import { Button } from '../../../components/ui';
import { invoiceService } from '../../../services/invoiceService';

const InvoiceCell = ({ lineItemId, onOpenDrawer }) => {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (lineItemId) {
      fetchInvoices();
    }
  }, [lineItemId]);

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await invoiceService.getInvoices(lineItemId);
      setInvoices(response.data || []);
    } catch (err) {
      console.error('Error fetching invoices:', err);
      setError('Failed to load invoices');
      setInvoices([]);
    } finally {
      setLoading(false);
    }
  };

  const handleClick = () => {
    if (onOpenDrawer) {
      onOpenDrawer(lineItemId, invoices);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-2">
        <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (error) {
    return (
      <Button
        variant="outline"
        size="sm"
        onClick={handleClick}
        className="text-red-600 border-red-300 hover:bg-red-50"
        aria-label="Error loading invoices - click to retry"
      >
        Error
      </Button>
    );
  }

  const invoiceCount = invoices.length;

  if (invoiceCount === 0) {
    return (
      <Button
        variant="outline"
        size="sm"
        onClick={handleClick}
        className="text-blue-600 border-blue-300 hover:bg-blue-50"
        aria-label="Add invoice"
      >
        Add Invoice
      </Button>
    );
  }

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={handleClick}
      className="relative text-blue-600 border-blue-300 hover:bg-blue-50"
      aria-label={`${invoiceCount} invoice${invoiceCount > 1 ? 's' : ''} - click to view`}
    >
      <span className="flex items-center gap-2">
        <svg
          className="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-medium text-white bg-blue-600 rounded-full">
          {invoiceCount}
        </span>
      </span>
    </Button>
  );
};

export default InvoiceCell;
