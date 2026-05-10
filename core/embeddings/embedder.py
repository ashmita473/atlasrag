# core/embeddings/embedder.py
import logging
from sentence_transformers import SentenceTransformer
from typing import List
from config.settings import settings
import numpy as np

logger = logging.getLogger(__name__)
 
class EmbeddingModel:
    _instance = None  # class-level cache — load model once
 
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            model_name = settings.embedding_model
            cls._instance.model = SentenceTransformer(
                model_name
            )
            logger.info(f"Loaded embedding model: {model_name}")
        return cls._instance
 
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        return self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True,  # cosine similarity = dot product
        )
 
    def embed_query(self, query: str) -> np.ndarray:
        logger.info(f"Embedding query: {query}")
        return self.embed_texts([query])[0]
