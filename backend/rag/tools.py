# rag/tools.py
from langchain.tools import tool
from sqlalchemy import text

from model.embedding import get_embedding
from model.pool import get_engine

_FOOD_CODE_SQL = """
    SELECT content,
           langchain_metadata->>'lv1' AS lv1,
           langchain_metadata->>'lv2' AS lv2,
           langchain_metadata->>'lv3' AS lv3,
           langchain_metadata->>'lv4' AS lv4,
           langchain_metadata->>'lv5' AS lv5,
           langchain_metadata->>'lv6' AS lv6,
           langchain_metadata->>'lv7' AS lv7,
           embedding <=> (:vec)::vector AS distance
    FROM foodsafety_fd_cd
    ORDER BY embedding <=> (:vec)::vector
    LIMIT :k
"""

_LEVEL_KEYS = ("lv1", "lv2", "lv3", "lv4", "lv5", "lv6", "lv7")


def _search(sql: str, query: str, k: int) -> list[dict]:
    params = {"vec": str(get_embedding().embed_query(query)), "k": k}
    with get_engine().connect() as conn:
        return conn.execute(text(sql), params).mappings().all()


@tool
def search_food_code(query: str, k: int = 5) -> str:
    """식품공전에서 식품 유형별 정의, 원료, 제조·가공기준, 규격, 시험방법을 검색한다."""
    rows = _search(_FOOD_CODE_SQL, query, k)
    if not rows:
        return "검색 결과가 없습니다."
    parts = []
    for r in rows:
        path = " > ".join(v for v in (r[key] for key in _LEVEL_KEYS) if v)
        parts.append(f"[{path}] (dist={r['distance']:.4f})\n{r['content']}")
    return "\n\n---\n\n".join(parts)
