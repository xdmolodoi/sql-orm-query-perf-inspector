import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./inspector.db")
    slow_query_ms: float = float(os.getenv("SLOW_QUERY_MS", "100"))
    n1_threshold: int = int(os.getenv("N1_THRESHOLD", "3"))
    query_history_limit: int = int(os.getenv("QUERY_HISTORY_LIMIT", "500"))
    n1_window_seconds: float = float(os.getenv("N1_WINDOW_SECONDS", "10"))

settings = Settings()
