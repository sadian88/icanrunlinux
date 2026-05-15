import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
EMBEDDINGS_API_URL = os.getenv("EMBEDDINGS_API_URL", "https://api.openai.com/v1")
EMBEDDINGS_API_KEY = os.getenv("EMBEDDINGS_API_KEY", "")
EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", "text-embedding-3-small")
EMBEDDINGS_DIMENSIONS = int(os.getenv("EMBEDDINGS_DIMENSIONS", "1536") or 1536)

# LLM config (DeepSeek via OpenRouter)
LLM_API_URL = os.getenv("LLM_API_URL", "https://openrouter.ai/api/v1/chat/completions")
LLM_API_KEY = os.getenv("LLM_API_KEY", EMBEDDINGS_API_KEY)
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-chat")

# Matching threshold: below this we fallback to LLM
MATCH_THRESHOLD = float(os.getenv("MATCH_THRESHOLD", "0.5"))

# AI cache: minimum similarity to reuse a cached query
AI_CACHE_THRESHOLD = float(os.getenv("AI_CACHE_THRESHOLD", "0.92"))
