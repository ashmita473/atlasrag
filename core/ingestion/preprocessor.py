# core/ingestion/preprocessor.py
import re
from langchain.schema import Document
from typing import List
 
 # Cleans noisy raw text before chunking and embedding
class TextPreprocessor:
    def clean(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)       # collapse whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)  # max 2 newlines
        text = text.encode('utf-8', 'ignore').decode('utf-8')  # strip bad chars
        return text.strip()
 
    def process_documents(self, docs: List[Document]) -> List[Document]:
        cleaned = []
        for doc in docs:
            cleaned_text = self.clean(doc.page_content)

            cleaned_doc = Document(
            page_content=cleaned_text,
            metadata=doc.metadata
            )
            if len(cleaned_text) > 50:
                cleaned.append(cleaned_doc)
        return cleaned
