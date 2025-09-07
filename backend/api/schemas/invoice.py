"""Pydantic schemas for invoice operations."""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class InvoiceBase(BaseModel):
    """Base invoice schema."""
    line_item_id: int
    file_name: str
    mime_type: str
    file_size: int = Field(..., gt=0, le=10485760)  # Max 10MB
    
class InvoiceCreate(InvoiceBase):
    """Schema for creating a new invoice."""
    pass

class InvoiceUploadBegin(BaseModel):
    """Schema for beginning an invoice upload."""
    line_item_id: int
    file_name: str
    mime_type: str = Field(..., pattern=r'^(application/pdf|image/(png|jpeg|jpg))$')
    file_size: int = Field(..., gt=0, le=10485760)  # Max 10MB

class InvoiceUploadComplete(BaseModel):
    """Schema for completing an invoice upload."""
    storage_path: str

class InvoiceOut(InvoiceBase):
    """Schema for invoice responses."""
    id: int
    user_id: str
    storage_path: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class InvoiceViewUrl(BaseModel):
    """Schema for invoice view URL response."""
    view_url: str
    expires_at: datetime

class InvoiceUploadSession(BaseModel):
    """Schema for upload session response."""
    invoice_id: int
    upload_url: str
    expires_at: datetime
