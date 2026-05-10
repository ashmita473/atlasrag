import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from core.embeddings.embedder import EmbeddingModel


embedder = EmbeddingModel()

sentences = [
    "Machine learning enables computers to learn from data.",
    "Neural networks are inspired by the human brain.",
    "Paris is the capital of France.",
]

embeddings = embedder.embed_texts(sentences)

print(f"Embedding shape: {embeddings.shape}")

print("\nFirst embedding preview:\n")
print(embeddings[0][:10])