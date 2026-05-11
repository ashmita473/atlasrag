# core/retrieval/retriever.py
from typing import List, Tuple
from langchain.schema import Document
from core.vectorstore.faiss_store import FAISSVectorStore
from core.embeddings.embedder import EmbeddingModel
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Handles semantic retrieval and diversity-aware MMR retrieval
class Retriever:
    def __init__(self, store: FAISSVectorStore):
        self.store = store
        self.embedder = EmbeddingModel()
 
    def top_k(self, query: str, k: int = 5) -> List[Document]:
        if self.store.index is None:
            return []
        results = self.store.similarity_search(query, k=k)
        logger.info(f"Retrieved {len(results)} documents using Top-K")
        return [doc for doc, _ in results]
        
    


    def mmr(self, query: str, k: int = 5,
            fetch_k: int = 20, lambda_mult: float = 0.5) -> List[Document]:
        if self.store.index is None:
            return []
        # Fetch a larger candidate set, then select diverse subset
        candidates = self.store.similarity_search(query, k=fetch_k)
        if not candidates:
            return []
 
        qvec = self.embedder.embed_query(query)
        selected, selected_vecs = [], []
        candidate_docs  = [doc  for doc, _ in candidates]
        candidate_vecs  = self.embedder.embed_texts(
            [d.page_content for d in candidate_docs]
        )
 
        while len(selected) < k and candidate_docs:
            if not selected_vecs:
                # First pick: highest similarity to query
                scores = candidate_vecs @ qvec
                best_idx = int(np.argmax(scores))
            else:
                rel_scores = candidate_vecs @ qvec
                div_scores = np.max(candidate_vecs @ np.array(selected_vecs).T, axis=1)
                # Balance relevance against diversity
                mmr_scores = lambda_mult * rel_scores - (1 - lambda_mult) * div_scores
                best_idx   = int(np.argmax(mmr_scores))
 
            selected.append(candidate_docs.pop(best_idx))
            selected_vecs.append(candidate_vecs[best_idx])
            candidate_vecs = np.delete(candidate_vecs, best_idx, axis=0)
        logger.info(f"Retrieved {len(selected)} documents using MMR")
        return selected
