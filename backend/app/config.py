import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = "Loan Rate Tracker"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://frontend:3000",
        "*",
    ]

    # Cache TTL in seconds (30 minutes)
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "1800"))
    CACHE_MAXSIZE: int = int(os.getenv("CACHE_MAXSIZE", "100"))

    # HTTP request timeout
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "10"))

    # OpenAI LLM settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

    # HTTP headers for scraping
    DEFAULT_HEADERS: dict = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }


settings = Settings()
