# config/settings.py
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
 
class Settings(BaseSettings):
    # LLM
    openrouter_api_key: str = Field(..., env='OPENROUTER_API_KEY')
    openrouter_base_url: str = Field(..., env='OPENROUTER_BASE_URL')
    default_model: str = Field('mistralai/mixtral-8x7b-instruct', env='DEFAULT_MODEL')
 
    # Embeddings
    embedding_model: str = Field('all-MiniLM-L6-v2', env='EMBEDDING_MODEL')
 
    # Retrieval
    chunk_size: int = Field(512, env='CHUNK_SIZE')
    chunk_overlap: int = Field(64, env='CHUNK_OVERLAP')
    top_k_retrieval: int = Field(5, env='TOP_K_RETRIEVAL')
 
    # Database
    db_url: str = Field('sqlite:///./edumind.db', env='DB_URL')
    secret_key: str = Field(..., env='SECRET_KEY')
 
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False
 
 
@lru_cache()   # Singleton — reads .env only once
def get_settings() -> Settings:
    return Settings()
settings = get_settings()
