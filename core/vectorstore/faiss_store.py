# core/vectorstore/faiss_store.py
import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple
from langchain.schema import Document
from core.embeddings.embedder import EmbeddingModel
import logging
 
logger = logging.getLogger(__name__)

# Stores and retrieves semantic document vectors using FAISS

class FAISSVectorStore:
    def __init__(self, index_path: str = 'data/faiss_indexes/default'):
        self.index_path = Path(index_path)
        self.embedder = EmbeddingModel()
        self.index: faiss.Index | None = None
        self.documents: List[Document] = []  # parallel to index rows
 
    def add_documents(self, docs: List[Document]) -> None:
        texts = [d.page_content for d in docs]
        vectors = self.embedder.embed_texts(texts).astype('float32')
 
        if self.index is None:
            dim = vectors.shape[1]
            self.index = faiss.IndexFlatIP(dim)  # IP = inner product (cosine on normalised vecs)
 
        self.index.add(vectors)
        self.documents.extend(docs)
        logger.info(f'Index now has {self.index.ntotal} vectors')
 
    def similarity_search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        if self.index is None:
            raise ValueError("FAISS index is empty.")
        qvec = self.embedder.embed_query(query).astype('float32').reshape(1, -1)

        k = min(k, len(self.documents))
        scores, indices = self.index.search(qvec, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:
                results.append((self.documents[idx], float(score)))
        return results
 
    def save(self) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path) + '.index')
        with open(str(self.index_path) + '.docs', 'wb') as f:
            pickle.dump(self.documents, f)
            logger.info(
                f"Saved FAISS index to {self.index_path}"
            )
 
    def load(self) -> None:
        self.index = faiss.read_index(str(self.index_path) + '.index')
        with open(str(self.index_path) + '.docs', 'rb') as f:
            self.documents = pickle.load(f)
        logger.info(f'Loaded index with {self.index.ntotal} vectors')
