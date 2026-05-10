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


loader = DocumentLoader()
preprocessor = TextPreprocessor()
chunker = TextChunker()

vectorstore = FAISSVectorStore()


document = loader.load_file("sample.pdf")

clean_docs = preprocessor.process_documents(
    document.pages
)

chunks = chunker.split(clean_docs)


vectorstore.add_documents(chunks)

print(f"Indexed chunks: {len(chunks)}")


results = vectorstore.similarity_search(
    "What is the title of the internship report?",
    k=3
)

print("\nTop Results:\n")

for i, (doc, score) in enumerate(results):

    print(f"\nResult {i + 1}")
    print(f"Score: {score:.4f}")

    print(doc.page_content[:300])

