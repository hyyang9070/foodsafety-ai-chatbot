# core/config.py
from dotenv import load_dotenv

load_dotenv()

CONNECTION_STRING = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"
TABLE_NAME = "food_code_vectors"
EMBEDDING_MODEL = "voyage-3-large"
CHAT_MODEL = "anthropic:claude-sonnet-4-6"
CORS_ORIGINS = ["http://localhost:5173"]