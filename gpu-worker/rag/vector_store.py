import faiss
import numpy as np
import pickle
import os


class VectorStore:
    def __init__(self, dimensions=384):
        self.dimensions = dimensions
        self.index = faiss.IndexFlatL2(dimensions)
        self.documents = []

    def addDocument(self, embedding, document):
        if not document or embedding is None:
            raise ValueError("Document and embedding cannot be empty")

        embedding = np.array(embedding).astype(np.float32)

        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)

        if embedding.shape[1] != self.dimensions:
            raise ValueError(f"Embedding dimension must be {self.dimensions}")

        self.index.add(embedding)
        self.documents.append(document)

    def search(self, queryEmbedding, topK=5):
        if self.index.ntotal == 0:
            return []

        queryEmbedding = np.array(queryEmbedding).astype(np.float32)

        if queryEmbedding.ndim == 1:
            queryEmbedding = queryEmbedding.reshape(1, -1)

        topK = min(topK, self.index.ntotal)

        distances, indices = self.index.search(queryEmbedding, topK)

        results = []

        for distance, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue

            results.append({
                "document": self.documents[int(idx)],
                "distance": float(distance),
                "index": int(idx)
            })

        return results

    def save(self, folderPath="data/vector_index"):
        os.makedirs(folderPath, exist_ok=True)

        faiss.write_index(self.index, os.path.join(folderPath, "index.faiss"))

        with open(os.path.join(folderPath, "documents.pkl"), "wb") as file:
            pickle.dump(self.documents, file)

    def load(self, folderPath="data/vector_index"):
        indexPath = os.path.join(folderPath, "index.faiss")
        documentsPath = os.path.join(folderPath, "documents.pkl")

        if not os.path.exists(indexPath) or not os.path.exists(documentsPath):
            return False

        self.index = faiss.read_index(indexPath)

        with open(documentsPath, "rb") as file:
            self.documents = pickle.load(file)

        return True

    def getDocumentCount(self):
        return len(self.documents)

    def clear(self):
        self.index = faiss.IndexFlatL2(self.dimensions)
        self.documents = []


vectorStore = VectorStore()