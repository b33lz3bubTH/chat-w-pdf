from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.core.tenant.service import TenantService, PDFProcessingService
from src.datasource.vector import VectorStoreService

app = FastAPI(
    title="Multi-Tenant PDF Store",
    description="Manage tenants, upload PDFs, and query documents.",
    version="1.0.0"
)

tenant_service = TenantService()
pdf_service = PDFProcessingService()
vector_service = VectorStoreService()

class TenantCreateRequest(BaseModel):
    name: str

class PDFUploadRequest(BaseModel):
    pdf_url: str

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/tenants/")
def create_tenant(request: TenantCreateRequest):
    tenant_id = tenant_service.create_tenant(request.name)
    return {"tenant_id": tenant_id, "message": "Tenant created successfully."}

@app.post("/tenants/{tenant_id}/pdfs/")
def upload_pdf(tenant_id: str, request: PDFUploadRequest):
    if not tenant_service.get_tenant(tenant_id):
        raise HTTPException(status_code=404, detail="Tenant not found.")

    try:
        documents = pdf_service.process_pdf(request.pdf_url, tenant_id)
        vector_service.store_documents(tenant_id, documents)
        return {"message": "PDF processed and stored successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/tenants/{tenant_id}/query/")
def query_documents(tenant_id: str, request: QueryRequest):
    if not tenant_service.get_tenant(tenant_id):
        raise HTTPException(status_code=404, detail="Tenant not found.")

    results = vector_service.retrieve_documents(tenant_id, request.query, request.top_k)
    if not results:
        return {"message": "No relevant documents found.", "results": []}
    
    return {"results": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9900)
