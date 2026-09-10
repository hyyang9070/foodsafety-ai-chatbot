# rag/agent.py
from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import InMemorySaver

from core.config import CHAT_MODEL
from rag.tools import search_food_code

MODEL_TEMPERATURE = 0.1

SYSTEM_PROMPT = (
    "너는 대한민국 식품 기준·규격 전문 어시스턴트다.\n\n"
    "도구 사용 원칙:\n"
    "- 식품 유형의 정의, 원료, 제조·가공기준, 규격, 시험방법 등 기준·규격 질문에는 "
    "search_food_code 도구를 사용하라.\n"
    "- 시중에 유통되는 개별 제품 정보(제품명, 제조사 등)는 검색할 수 없다. "
    "해당 질문에는 조회 가능한 범위가 식품공전 기준·규격뿐이라고 밝혀라.\n\n"
    "답변 원칙:\n"
    "- 반드시 도구로 검색한 근거를 바탕으로 답하고, 출처 분류 경로를 함께 제시하라.\n"
    "- 검색 결과에 없는 내용은 추측하지 말고 검색 결과에서 확인되지 않는다고 명시하라.\n"
    "- 첫 검색 결과가 불충분하면 검색어를 바꿔 다시 검색하라."
    "\n\n출력 형식:\n"
    "- 이모지를 절대 사용하지 마라.\n"
    "- 불필요한 감탄사나 장식 없이 사실 위주로 간결하게 답하라."
)

chat_model = ChatAnthropic(
    model=CHAT_MODEL.removeprefix("anthropic:"),
    temperature=MODEL_TEMPERATURE,
)

agent = create_agent(
    model=chat_model,
    tools=[search_food_code],
    system_prompt=SYSTEM_PROMPT,
    middleware=[
        ToolCallLimitMiddleware(run_limit=6),
        # 툴별 개별 제한 (선택)
        ToolCallLimitMiddleware(tool_name="search_food_code", run_limit=3),
    ],
    checkpointer=InMemorySaver(),
)
