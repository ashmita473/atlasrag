# core/llm/openrouter.py
from openai import OpenAI
from typing import List
from .base import BaseLLM, Message, LLMResponse
from config.settings import settings
import logging
 
logger = logging.getLogger(__name__)
 
class OpenRouterLLM(BaseLLM):
    def __init__(self, model: str | None = None):
        self.model = model or settings.default_model
        
        self.client = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
        )
 
    def chat(self, messages: List[Message],
             temperature: float = 0.7,
             max_tokens: int = 1024) -> LLMResponse:
        formatted_messages = [{'role': m.role, 'content': m.content}
                     for m in messages]
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            usage = response.usage
            return LLMResponse(
                content=response.choices[0].message.content,
                model=self.model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
            )
        except Exception as e:
            logger.error(f'OpenRouter API call failed: {e}')
            raise
 
    def get_model_name(self) -> str:
        return self.model
