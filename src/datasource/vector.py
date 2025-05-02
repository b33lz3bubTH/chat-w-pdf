from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

class VectorStoreService:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.persist_directory = persist_directory

    def store_documents(self, tenant_id: str, documents: list):
        collection_name = f"tenant_{tenant_id}"
        vector_store = Chroma.from_documents(
            documents,
            self.embedding_model,
            persist_directory=self.persist_directory,
            collection_name=collection_name
        )
        vector_store.persist()

    def retrieve_documents(self, tenant_id: str, query: str) -> list:
        collection_name = f"tenant_{tenant_id}"
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embedding_model,
            persist_directory=self.persist_directory
        )
        retriever = vector_store.as_retriever()
        return retriever.get_relevant_documents(query)
