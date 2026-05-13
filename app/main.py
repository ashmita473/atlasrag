# app/main.py
import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

import streamlit as st
from pathlib import Path
import tempfile
from core.ingestion.loader import DocumentLoader
from core.ingestion.preprocessor import TextPreprocessor
from core.ingestion.chunker import TextChunker
from core.vectorstore.faiss_store import FAISSVectorStore
from core.pipelines.rag_chain import RAGChain
 
st.set_page_config(page_title='EduMind', page_icon='🧠', layout='wide')
 
# ── Initialise session state ──────────────────────────────────────────
if 'store' not in st.session_state:
    st.session_state.store = FAISSVectorStore()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'rag_chain' not in st.session_state:
    st.session_state.rag_chain = None
 
# ── Sidebar: Upload ───────────────────────────────────────────────────
with st.sidebar:
    st.title('🧠 EduMind')
    st.caption('RAG-Powered AI Tutor')
    uploaded = st.file_uploader(
        'Upload study material',
        type=['pdf', 'docx'],
        accept_multiple_files=True
    )
    if st.button('Index Documents'):

        if not uploaded:
            st.warning("Please upload at least one document.")

        else:
            loader= DocumentLoader()
            preprocessor = TextPreprocessor()
            chunker     = TextChunker()
            with st.spinner('Processing...'):
                for file in uploaded:
                    with tempfile.NamedTemporaryFile(suffix=Path(file.name).suffix,
                                                delete=False) as tmp:
                        tmp.write(file.read())
                        loaded = loader.load_file(tmp.name)
                        clean  = preprocessor.process_documents(loaded.pages)
                        chunks = chunker.split(clean)
                        if len(chunks) == 0:
                            continue
                        st.session_state.store.add_documents(chunks)
                st.session_state.rag_chain = RAGChain(st.session_state.store)
            st.success(
                f"Successfully indexed {len(uploaded)} document(s)."
            )
 
# ── Main chat area ────────────────────────────────────────────────────
st.title('Ask Your Study Material')
for msg in st.session_state.chat_history:
    with st.chat_message(msg['role']):
        st.write(msg['content'])
 
if prompt := st.chat_input('Ask a question about your documents...'):
    if st.session_state.rag_chain is None:
        st.warning('Please upload and index documents first.')
    else:
        st.session_state.chat_history.append({'role': 'user', 'content': prompt})
        with st.chat_message('user'):
            st.write(prompt)
        with st.chat_message('assistant'):
            with st.spinner('Thinking...'):
                result = st.session_state.rag_chain.query(
                    prompt, st.session_state.chat_history
                )
            st.write(result.answer)
            st.caption(
                f"Model: {result.model} | Tokens Used: {result.tokens_used}"
            )
            with st.expander('📚 Sources'):
                for i, src in enumerate(result.sources):
                    st.caption(f'[Source {i+1}] {src.metadata.get("filename", "Unknown")}')
                    st.code(
                        src.page_content[:300] + '...',
                        language=None
                    )
        st.session_state.chat_history.append(
            {'role': 'assistant', 'content': result.answer}
        )
