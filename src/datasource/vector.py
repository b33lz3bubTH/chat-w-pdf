from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

class VectorStoreService:
    def __init__(self):
        self.embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.client = Chroma(
            embedding_function=self.embedding_model,
            persist_directory="db"
        )

    def store_documents(self, tenant_id: str, documents: list):
        collection_name = f"tenant_{tenant_id}"
        collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"tenant_id": tenant_id}
        )
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        ids = [f"{tenant_id}_doc_{i}" for i in range(len(texts))]
        embeddings = self.embedding_model.embed_documents(texts)
        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings
        )

    def retrieve_documents(self, tenant_id: str, query: str, top_k: int = 5) -> list:
        collection_name = f"tenant_{tenant_id}"
        try:
            collection = self.client.get_collection(name=collection_name)
        except Exception:
            print(f"Collection {collection_name} does not exist.")
            return []
        query_embedding = self.embedding_model.embed_query(query)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        documents = []
        if not results.get("ids") or not results["ids"][0]:
            print("No results found")
            return []
        for i in range(len(results["ids"][0])):
            doc_text = results["documents"][0][i]
            metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
            distance = results["distances"][0][i] if results.get("distances") else None
            if distance is not None:
                metadata["similarity"] = 1 - distance
            documents.append({"page_content": doc_text, "metadata": metadata})
        return documents
