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


loader = DocumentLoader()
preprocessor = TextPreprocessor()
chunker = TextChunker()

document = loader.load_file("sample.pdf")

clean_docs = preprocessor.process_documents(
    document.pages
)

chunks = chunker.split(clean_docs)

print(f"Total chunks created: {len(chunks)}")

print("\nFirst chunk preview:\n")
print(chunks[0].page_content[:500])

print("\nChunk metadata:\n")
print(chunks[0].metadata)