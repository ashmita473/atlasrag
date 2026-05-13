import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from core.ingestion.loader import DocumentLoader
from core.ingestion.preprocessor import TextPreprocessor
from core.ingestion.chunker import TextChunker
from core.vectorstore.faiss_store import FAISSVectorStore
from core.pipelines.rag_chain import RAGChain


loader = DocumentLoader()
preprocessor = TextPreprocessor()
chunker = TextChunker()

store = FAISSVectorStore()


document = loader.load_file("sample.pdf")

clean_docs = preprocessor.process_documents(
    document.pages
)

chunks = chunker.split(clean_docs)

store.add_documents(chunks)


rag = RAGChain(store)


response = rag.query(
    "What skills were learned during the internship?"
)


print("\n=== RAG ANSWER ===\n")

print(response.answer)

print("\n=== SOURCES ===\n")

for i, source in enumerate(response.sources):

    print(f"\nSource {i + 1}\n")

    print(source.page_content[:300])

print(f"\nModel Used: {response.model}")

print(f"Tokens Used: {response.tokens_used}")