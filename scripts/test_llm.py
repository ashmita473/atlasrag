import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm.openrouter import OpenRouterLLM
from core.llm.base import Message
from core.llm.base import Message

llm = OpenRouterLLM()

response = llm.chat([
    Message(
        role='system',
        content='You are a helpful AI tutor.'
    ),
    Message(
        role='user',
        content="Explain Newton's first law in one sentence."
    )
])

print(f'Model: {response.model}')
print(f'Answer: {response.content}')
print(f'Tokens used: {response.prompt_tokens + response.completion_tokens}')