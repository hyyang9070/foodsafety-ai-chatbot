# api/schemas.py
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default"

class ChatResponse(BaseModel):
    answer: str