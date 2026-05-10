# core/ingestion/loader.py
from dataclasses import dataclass, field
from typing import List
from pathlib import Path
import logging
 
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    WebBaseLoader,
)
from langchain.schema import Document
 
logger = logging.getLogger(__name__)
 
@dataclass
class LoadedDocument:
    source: str                        # file path or URL
    doc_type: str                      # 'pdf' | 'docx' | 'url'
    pages: List[Document] = field(default_factory=list)
    metadata: dict[str, str | int] = field(default_factory=dict)

# Handles ingestion of PDF, DOCX, and web documents
class DocumentLoader:
    SUPPORTED = {'.pdf', '.docx', '.doc'}
 
    def load_file(self, path: str) -> LoadedDocument:
        p = Path(path)
        ext = p.suffix.lower()
        if ext not in self.SUPPORTED:
            raise ValueError(f'Unsupported file type: {ext}')
 
        loader = PyPDFLoader(str(p)) if ext == '.pdf' else Docx2txtLoader(str(p))
        docs = loader.load()
        logger.info(
        f"Loaded {len(docs)} pages from file: {p.name}"
        )
 
        return LoadedDocument(
            source=str(p),
            doc_type=ext.lstrip('.'),
            pages=docs,
            metadata={'filename': p.name, 'pages': len(docs)}
        )
 
    def load_url(self, url: str) -> LoadedDocument:
        loader = WebBaseLoader(url)
        docs = loader.load()
        logger.info(f"Loaded web content from URL: {url}")
        return LoadedDocument(
            source=url,
            doc_type='url',
            pages=docs,
            metadata={'url': url}
        )
