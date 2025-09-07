"""Invoice management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
import logging
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from api.core.supabase import get_current_user, supabase
from api.core.database import get_db
from api.models.invoice import LineItemInvoice, InvoiceStatusEnum
from api.models.forecast import ForecastLineItem
from api.schemas.invoice import (
    InvoiceUploadBegin, 
    InvoiceUploadComplete, 
    InvoiceOut, 
    InvoiceViewUrl, 
    InvoiceUploadSession
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# File validation constants
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'image/png', 
    'image/jpeg',
    'image/jpg'
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/line-items/{line_item_id}/invoices:begin-upload", response_model=InvoiceUploadSession)
async def begin_invoice_upload(
    line_item_id: int,
    upload_request: InvoiceUploadBegin,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Begin a two-phase invoice upload process."""
    logger.info(f"Beginning invoice upload for line item {line_item_id} by user {current_user['id']}")
    
    # Validate file type and size
    if upload_request.mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {upload_request.mime_type} not allowed. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}"
        )
    
    if upload_request.file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size {upload_request.file_size} exceeds maximum of {MAX_FILE_SIZE} bytes"
        )
    
    # Verify line item exists and user has access
    user_uuid = uuid.UUID(current_user['id']) if isinstance(current_user['id'], str) else current_user['id']
    line_item = db.query(ForecastLineItem).filter(
        ForecastLineItem.id == line_item_id,
        ForecastLineItem.user_id == user_uuid
    ).first()
    
    if not line_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Line item not found or access denied"
        )
    
    try:
        # Generate unique invoice ID and storage path
        invoice_id = str(uuid.uuid4())
        file_extension = upload_request.file_name.split('.')[-1] if '.' in upload_request.file_name else ''
        storage_path = f"invoices/{line_item.project_id}/{line_item_id}/{invoice_id}.{file_extension}"
        
        # Create pending invoice record
        invoice = LineItemInvoice(
            user_id=user_uuid,
            line_item_id=line_item_id,
            file_name=upload_request.file_name,
            mime_type=upload_request.mime_type,
            file_size=upload_request.file_size,
            storage_path=storage_path,
            status=InvoiceStatusEnum.pending
        )
        
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        # Generate presigned upload URL (10 minutes expiry)
        expires_in = 600  # 10 minutes
        upload_url = supabase.storage.from_('invoices').create_signed_upload_url(storage_path, expires_in)
        
        if not upload_url or 'signedURL' not in upload_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate upload URL"
            )
        
        logger.info(f"Created invoice upload session {invoice.id} for line item {line_item_id}")
        
        return InvoiceUploadSession(
            invoice_id=invoice.id,
            upload_url=upload_url['signedURL'],
            expires_at=datetime.utcnow() + timedelta(seconds=expires_in)
        )
        
    except Exception as e:
        logger.error(f"Error beginning invoice upload: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to begin upload session"
        )

@router.post("/line-items/{line_item_id}/invoices/{invoice_id}:complete", response_model=InvoiceOut)
async def complete_invoice_upload(
    line_item_id: int,
    invoice_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete the invoice upload process."""
    logger.info(f"Completing invoice upload {invoice_id} for line item {line_item_id}")
    
    user_uuid = uuid.UUID(current_user['id']) if isinstance(current_user['id'], str) else current_user['id']
    # Find the pending invoice
    invoice = db.query(LineItemInvoice).filter(
        LineItemInvoice.id == invoice_id,
        LineItemInvoice.line_item_id == line_item_id,
        LineItemInvoice.user_id == user_uuid,
    ).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found or access denied"
        )
    
    if invoice.status != InvoiceStatusEnum.pending:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Invoice is not in pending status (current: {invoice.status})"
        )
    
    try:
        # Verify file exists in storage
        file_info = supabase.storage.from_('invoices').get_public_url(invoice.storage_path)
        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File not found in storage. Upload may have failed."
            )
        
        # Update invoice status to uploaded
        invoice.status = InvoiceStatusEnum.uploaded
        db.commit()
        db.refresh(invoice)
        
        logger.info(f"Successfully completed invoice upload {invoice_id}")
        return InvoiceOut.from_orm(invoice)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing invoice upload: {str(e)}")
        # Mark as failed
        invoice.status = InvoiceStatusEnum.failed
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete upload"
        )

@router.get("/line-items/{line_item_id}/invoices", response_model=List[InvoiceOut])
async def list_invoices(
    line_item_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all invoices for a line item."""
    logger.info(f"Listing invoices for line item {line_item_id}")
    
    user_uuid = uuid.UUID(current_user['id']) if isinstance(current_user['id'], str) else current_user['id']
    # Verify line item exists and user has access
    line_item = db.query(ForecastLineItem).filter(
        ForecastLineItem.id == line_item_id,
        ForecastLineItem.user_id == user_uuid
    ).first()
    
    if not line_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Line item not found or access denied"
        )
    
    # Get all invoices for this line item
    invoices = db.query(LineItemInvoice).filter(
        LineItemInvoice.line_item_id == line_item_id,
        LineItemInvoice.user_id == user_uuid,
        LineItemInvoice.status == InvoiceStatusEnum.uploaded
    ).all()
    
    return [InvoiceOut.from_orm(invoice) for invoice in invoices]

@router.get("/line-items/{line_item_id}/invoices/{invoice_id}:view-url", response_model=InvoiceViewUrl)
async def get_invoice_view_url(
    line_item_id: int,
    invoice_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a signed URL to view an invoice."""
    logger.info(f"Getting view URL for invoice {invoice_id}")
    
    user_uuid = uuid.UUID(current_user['id']) if isinstance(current_user['id'], str) else current_user['id']
    # Find the invoice
    invoice = db.query(LineItemInvoice).filter(
        LineItemInvoice.id == invoice_id,
        LineItemInvoice.line_item_id == line_item_id,
        LineItemInvoice.user_id == user_uuid,
        LineItemInvoice.status == InvoiceStatusEnum.uploaded
    ).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found or access denied"
        )
    
    try:
        # Generate signed URL (10 minutes expiry)
        expires_in = 600  # 10 minutes
        signed_url = supabase.storage.from_('invoices').create_signed_url(
            invoice.storage_path, 
            expires_in
        )
        
        if not signed_url or 'signedURL' not in signed_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate view URL"
            )
        
        return InvoiceViewUrl(
            view_url=signed_url['signedURL'],
            expires_at=datetime.utcnow() + timedelta(seconds=expires_in)
        )
        
    except Exception as e:
        logger.error(f"Error generating view URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate view URL"
        )

@router.delete("/line-items/{line_item_id}/invoices/{invoice_id}")
async def delete_invoice(
    line_item_id: int,
    invoice_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an invoice."""
    logger.info(f"Deleting invoice {invoice_id} for line item {line_item_id}")
    
    user_uuid = uuid.UUID(current_user['id']) if isinstance(current_user['id'], str) else current_user['id']
    # Find the invoice
    invoice = db.query(LineItemInvoice).filter(
        LineItemInvoice.id == invoice_id,
        LineItemInvoice.line_item_id == line_item_id,
        LineItemInvoice.user_id == user_uuid
    ).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found or access denied"
        )
    
    try:
        # Delete file from storage
        try:
            supabase.storage.from_('invoices').remove([invoice.storage_path])
        except Exception as e:
            logger.warning(f"Failed to delete file from storage: {str(e)}")
            # Continue with database deletion even if storage deletion fails
        
        # Delete database record
        db.delete(invoice)
        db.commit()
        
        logger.info(f"Successfully deleted invoice {invoice_id}")
        return {"message": "Invoice deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting invoice: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete invoice"
        )
