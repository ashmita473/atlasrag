from dataclasses import dataclass
from typing import List
import logging

from langchain.schema import Document

from core.vectorstore.faiss_store import FAISSVectorStore
from core.retrieval.retriever import Retriever
from core.llm.openrouter import OpenRouterLLM
from core.llm.base import LLMResponse
from core.prompts.tutor import build_rag_prompt

from config.settings import settings


logger = logging.getLogger(__name__)


@dataclass
class RAGResponse:

    answer: str
    sources: List[Document]
    model: str
    tokens_used: int


class RAGChain:

    def __init__(
        self,
        store: FAISSVectorStore
    ):

        self.retriever = Retriever(store)

        self.llm = OpenRouterLLM()

    def query(
        self,
        question: str,
        history: list | None = None
    ) -> RAGResponse:

        history = history or []

        logger.info(
            f"Processing RAG query: {question}"
        )

        # Step 1: Retrieve relevant context
        context = self.retriever.mmr(
            question,
            k=settings.top_k_retrieval
        )

        logger.info(
            f"Retrieved {len(context)} context chunks"
        )

        # Step 2: Build prompt
        messages = build_rag_prompt(
            context,
            question,
            history
        )

        # Step 3: Generate answer
        response: LLMResponse = self.llm.chat(
            messages
        )

        return RAGResponse(
            answer=response.content,
            sources=context,
            model=response.model,
            tokens_used=(
                response.prompt_tokens
                +
                response.completion_tokens
            ),
        )