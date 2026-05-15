import json
import logging

from typing import List

from langchain.schema import Document

from core.llm.openrouter import OpenRouterLLM
from core.llm.base import Message


logger = logging.getLogger(__name__)


QUIZ_PROMPT = """
Generate {n} multiple-choice questions from the context below.

Difficulty: {difficulty}
(easy | medium | hard)

Return ONLY valid raw JSON.

Do NOT use markdown.
Do NOT wrap response in ```json.

Each item must follow this format:

[
  {{
    "question": "...",
    "options": ["A", "B", "C", "D"],
    "answer": "A",
    "explanation": "..."
  }}
]

Context:
{context}
"""


class QuizChain:

    def __init__(self):

        self.llm = OpenRouterLLM()

    def generate(
        self,
        docs: List[Document],
        n: int = 5,
        difficulty: str = "medium"
    ) -> list:

        context = "\n\n".join(
            d.page_content
            for d in docs[:5]
        )

        prompt = QUIZ_PROMPT.format(
            n=n,
            difficulty=difficulty,
            context=context
        )

        response = self.llm.chat(
            [
                Message(
                    role="user",
                    content=prompt
                )
            ],
            temperature=0.3
        )
        content = response.content.strip()

        if content.startswith("```json"):
            content = content.replace("```json", "")

        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        try:

            quiz_data = json.loads(content)

            logger.info(
                f"Generated {len(quiz_data)} quiz questions"
            )

            return quiz_data

        except json.JSONDecodeError as e:

            logger.error(
                f"Quiz JSON parsing failed: {e}"
            )
            print("\nRAW MODEL OUTPUT:\n")
            print(content)

            return []