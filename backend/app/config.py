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

    # Google Gemini AI settings (primary)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    # OpenAI LLM settings (fallback)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")


settings = Settings()
