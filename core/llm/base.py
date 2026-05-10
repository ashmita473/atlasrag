# core/llm/base.py
from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass
 
@dataclass
class Message:
    role: str   # 'system' | 'user' | 'assistant'
    content: str
 
@dataclass
class LLMResponse:
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    
 # Abstract interface every LLM provider must implement
class BaseLLM(ABC):
    @abstractmethod
    def chat(self,
             messages: List[Message],
             temperature: float = 0.7,
             max_tokens: int = 1024) -> LLMResponse:
        pass
 
    @abstractmethod
    def get_model_name(self) -> str:
        pass
