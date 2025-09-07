"""Invoice model for line item invoice attachments."""

from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from .base import Base

class InvoiceStatusEnum(str, enum.Enum):
    """Enumeration for invoice status values."""
    pending = "pending"
    uploaded = "uploaded"
    failed = "failed"

class LineItemInvoice(Base):
    """Invoice model representing uploaded invoices for forecast line items."""
    __tablename__ = "line_item_invoices"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    line_item_id = Column(Integer, ForeignKey("forecast_line_items.id"), nullable=False)
    file_name = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    storage_path = Column(String, nullable=False)
    status = Column(Enum(InvoiceStatusEnum), default=InvoiceStatusEnum.pending)
    
    # Relationships
    line_item = relationship("ForecastLineItem", back_populates="invoices")
