import uuid
import os
import requests

from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


from src.datasource.sqlalchemy import SessionLocal
from src.datasource.models import Tenant, Document


class TenantService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    def create_tenant(self, tenant_name: str) -> str:
        tenant_id = uuid.uuid4()
        tenant = Tenant(tenant_id=tenant_id, tenant_name=tenant_name)
        with self.session_factory() as session:
            session.add(tenant)
            session.commit()
        return str(tenant_id)

    def get_tenant(self, tenant_id: str) -> dict | None:
        try:
            tenant_uuid = uuid.UUID(tenant_id)
            with self.session_factory() as session:
                tenant = session.query(Tenant).filter(Tenant.tenant_id == tenant_uuid).first()
                if tenant:
                    return {"tenant_id": str(tenant.tenant_id), "tenant_name": tenant.tenant_name}
        except ValueError:
            pass
        return None

# --- PDF Processing Service ---
class PDFProcessingService:
    def __init__(self, temp_dir: str = "/tmp", session_factory=SessionLocal):
        self.temp_dir = temp_dir
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        self.session_factory = session_factory

    def _download_pdf(self, pdf_url: str) -> str:
        response = requests.get(pdf_url)
        response.raise_for_status()
        pdf_id = str(uuid.uuid4())
        pdf_path = os.path.join(self.temp_dir, f"{pdf_id}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(response.content)
        return pdf_path

    def process_pdf(self, pdf_url: str, tenant_id: str) -> list:
        try:
            tenant_uuid = uuid.UUID(tenant_id)
        except ValueError:
            raise ValueError("Invalid tenant ID format")

        # Download and process PDF
        pdf_path = self._download_pdf(pdf_url)
        loader = PyMuPDFLoader(pdf_path)
        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)

        # Store document metadata
        with self.session_factory() as session:
            document = Document(tenant_id=tenant_uuid, pdf_url=pdf_url)
            session.add(document)
            session.commit()
            document_id = str(document.document_id)

        # Add metadata to chunks
        for chunk in chunks:
            chunk.metadata["tenant_id"] = tenant_id
            chunk.metadata["document_id"] = document_id

        # Clean up temporary file
        os.remove(pdf_path)
        return chunks
