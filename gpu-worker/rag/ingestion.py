from sentence_transformers import SentenceTransformer
from rag.vector_store import vectorStore
from common.config import MAX_CHUNK_SIZE

embeddingModel = SentenceTransformer("all-MiniLM-L6-v2")


def splitText(text, maxChunkSize=MAX_CHUNK_SIZE):
    words = text.split()
    chunks = []

    for i in range(0, len(words), maxChunkSize):
        chunk = " ".join(words[i:i + maxChunkSize])
        chunks.append(chunk)

    return chunks


def ingestDocuments(documents):
    if isinstance(documents, str):
        documents = [documents]

    chunks = []

    for document in documents:
        chunks.extend(splitText(document))

    if not chunks:
        raise ValueError("Document cannot be empty")

    embeddings = embeddingModel.encode(chunks)

    for chunk, embedding in zip(chunks, embeddings):
        vectorStore.addDocument(embedding, chunk)

    vectorStore.save()

    return len(chunks)