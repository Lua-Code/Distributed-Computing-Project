from sentence_transformers import SentenceTransformer
from rag.vector_store import vectorStore


embeddingModel = SentenceTransformer("all-MiniLM-L6-v2")
vectorStore.load()


def retrieveDocuments(query, topK=3):
    if not query:
        return []

    queryEmbedding = embeddingModel.encode([query])
    return vectorStore.search(queryEmbedding, topK)


def retrieveContext(query, topK=3):
    results = retrieveDocuments(query, topK)

    documents = [
        result["document"]
        for result in results
    ]

    return "\n".join(documents)