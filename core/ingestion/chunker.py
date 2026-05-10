# core/ingestion/chunker.py
from docx import settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List
from config.settings import settings
 
# Splits documents into overlapping chunks for retrieval 
class TextChunker:
    def __init__(self):
    
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=['\n\n', '\n', '. ', ' ', ''],
            length_function=len,
        )
 
    def split(self, docs: List[Document]) -> List[Document]:
        chunks = self.splitter.split_documents(docs)
        # Enrich metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata['chunk_id'] = i
            chunk.metadata['char_count'] = len(chunk.page_content)
        return chunks
