# core/config.py
from dotenv import load_dotenv

load_dotenv()

CONNECTION_STRING = "postgresql://neondb_owner:npg_KfIVNdlW0zU3@ep-sweet-grass-b3tcsojw.c-4.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
TABLE_NAME = "food_code_vectors"
EMBEDDING_MODEL = "voyage-3-large"
CHAT_MODEL = "anthropic:claude-sonnet-4-6"
CORS_ORIGINS = ["http://localhost:5173"]