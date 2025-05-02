
from src.core.tenant.service import TenantService, PDFProcessingService
from src.datasource.vector import VectorStoreService

class PDFStoreApp:
    def __init__(self):
        self.tenant_service = TenantService()
        self.pdf_service = PDFProcessingService()
        self.vector_service = VectorStoreService()

    def run(self):
        print("\n📄 Multi-Tenant PDF Store (SQLAlchemy)")
        print("Type 'exit' to quit.\n")

        while True:
            print("1. Create Tenant")
            print("2. Upload PDF")
            print("3. Query Documents")
            print("4. Exit")
            choice = input("\nSelect an option: ")

            if choice == "1":
                tenant_name = input("Enter tenant name: ")
                tenant_id = self.tenant_service.create_tenant(tenant_name)
                print(f"Tenant created with ID: {tenant_id}")

            elif choice == "2":
                tenant_id = input("Enter tenant ID: ")
                if not self.tenant_service.get_tenant(tenant_id):
                    print("Invalid tenant ID.")
                    continue
                pdf_url = input("Enter PDF URL: ")
                try:
                    documents = self.pdf_service.process_pdf(pdf_url, tenant_id)
                    self.vector_service.store_documents(tenant_id, documents)
                    print("PDF processed and stored successfully.")
                except Exception as e:
                    print(f"Error processing PDF: {e}")

            elif choice == "3":
                tenant_id = input("Enter tenant ID: ")
                if not self.tenant_service.get_tenant(tenant_id):
                    print("Invalid tenant ID.")
                    continue
                query = input("Enter your query: ")
                results = self.vector_service.retrieve_documents(tenant_id, query)
                if not results:
                    print("\n❌ No relevant documents found.\n")
                else:
                    print("\n📚 Retrieved Documents:")
                    for doc in results:
                        print(f"• Document ID: {doc.metadata['document_id']}")
                        print(f"  Content: {doc.page_content[:100]}...\n")

            elif choice == "4":
                print("👋 Bye!")
                break

            else:
                print("Invalid option.")

if __name__ == "__main__":
    app = PDFStoreApp()
    app.run()
