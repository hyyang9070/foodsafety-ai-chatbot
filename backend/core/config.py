import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL 환경 변수가 설정되지 않았습니다.")

# Neon이 제공하는 postgresql:// URL을 SQLAlchemy psycopg 3 형식으로 변환합니다.
CONNECTION_STRING = DATABASE_URL.replace(
    "postgresql://", "postgresql+psycopg://", 1
)
TABLE_NAME = "foodsafety_fd_cd"
EMBEDDING_MODEL = "voyage-3-large"
CHAT_MODEL = "anthropic:claude-sonnet-4-6"
CORS_ORIGINS = ["http://localhost:5173"]
