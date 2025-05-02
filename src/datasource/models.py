import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from .sqlalchemy import engine, Base


class Tenant(Base):
    __tablename__ = "tenants"
    tenant_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_name = Column(String, nullable=False)
    documents = relationship("Document", back_populates="tenant")

class Document(Base):
    __tablename__ = "documents"
    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False)
    pdf_url = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    tenant = relationship("Tenant", back_populates="documents")



Base.metadata.create_all(engine)
