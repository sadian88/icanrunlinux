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

# Rate limiting
RATE_LIMIT_MAX = int(os.getenv("RATE_LIMIT_MAX", "2"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # seconds (1 hour)

# Security
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
MAX_REQUEST_SIZE = int(os.getenv("MAX_REQUEST_SIZE", "10240"))  # 10KB

# Hardware validation keywords (must detect >= 2)
HARDWARE_KEYWORDS = [
    # English
    "ram",
    "cpu",
    "gpu",
    "ssd",
    "hdd",
    "nvme",
    "memory",
    "storage",
    "disk",
    "processor",
    "graphics",
    "display",
    "monitor",
    "laptop",
    "desktop",
    "pc",
    "hardware",
    "specs",
    "spec",
    "configuration",
    "intel",
    "amd",
    "nvidia",
    "ryzen",
    "threadripper",
    "athlon",
    "pentium",
    "celeron",
    "xeon",
    "core",
    "ghz",
    "thread",
    "core",
    "architecture",
    "mb",
    "tb",
    "x86_64",
    "aarch64",
    # Spanish
    "memoria",
    "procesador",
    "graficos",
    "almacenamiento",
    "pantalla",
    "portatil",
    "portátil",
    "escritorio",
    "equipo",
    "núcleos",
    "nucleos",
    "hilos",
    "tarjeta",
    "grafica",
    "gráfica",
]
