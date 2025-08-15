from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

class VectorStoreService:
    def __init__(self):
        self.embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})
        self.persist_directory = "db"

    def store_documents(self, tenant_id: str, documents: list):
        collection_name = f"tenant_{tenant_id}"
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        ids = [f"{tenant_id}_doc_{i}" for i in range(len(texts))]
        embeddings = self.embedding_model.embed_documents(texts)

        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embedding_model,
            persist_directory=self.persist_directory
        )
        vectorstore.add_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )
        vectorstore.persist()  # ensure it writes to disk

    def retrieve_documents(self, tenant_id: str, query: str, top_k: int = 5) -> list:
        collection_name = f"tenant_{tenant_id}"

        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embedding_model,
            persist_directory=self.persist_directory
        )
        query_embedding = self.embedding_model.embed_query(query)
        results = vectorstore.similarity_search_by_vector(
            query_embedding,
            k=top_k
        )
        documents = []
        for doc in results:
            doc_text = doc.page_content
            metadata = doc.metadata or {}
            documents.append({"page_content": doc_text, "metadata": metadata})
        return documents
