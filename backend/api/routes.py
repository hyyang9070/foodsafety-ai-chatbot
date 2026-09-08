# api/routes.py
from fastapi import APIRouter

from api.schemas import ChatRequest, ChatResponse
from rag.agent import agent

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": req.message}]},
        config={"configurable": {"thread_id": req.thread_id}},
    )
    print('에이전트 응답 확인 ')
    print(result)
    return ChatResponse(answer=result["messages"][-1].text)