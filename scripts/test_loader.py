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


loader = DocumentLoader()
preprocessor = TextPreprocessor()

document = loader.load_file("sample.pdf")

cleaned_docs = preprocessor.process_documents(
    document.pages
)

print(f"Loaded pages: {len(document.pages)}")
print(f"Cleaned pages: {len(cleaned_docs)}")

print("\nSample Content:\n")
print(cleaned_docs[0].page_content[:500])