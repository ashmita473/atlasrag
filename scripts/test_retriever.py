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
from core.retrieval.retriever import Retriever


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


retriever = Retriever(store)

query = "What skills were learned during the internship?"


print("\n=== TOP-K RETRIEVAL ===\n")

topk_docs = retriever.top_k(query, k=3)

for i, doc in enumerate(topk_docs):

    print(f"\nResult {i + 1}\n")

    print(doc.page_content[:300])


print("\n\n=== MMR RETRIEVAL ===\n")

mmr_docs = retriever.mmr(
    query,
    k=3,
    fetch_k=10,
    lambda_mult=0.5
)

for i, doc in enumerate(mmr_docs):

    print(f"\nResult {i + 1}\n")

    print(doc.page_content[:300])