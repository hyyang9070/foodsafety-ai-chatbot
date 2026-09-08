import asyncio
import sys

# Windows 환경일 때 psycopg 호환을 위한 Event Loop Policy 변경
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import json
from pathlib import Path

from langchain_core.documents import Document

from rag.store import get_store

# 작업 디렉터리와 무관하게 프로젝트 루트의 data/doc.jsonl을 가리킴
DOC_PATH = Path(__file__).resolve().parent.parent / "data" / "doc.jsonl"


def load(table_name = "foodsafety_fd_cd", doc_path: Path = DOC_PATH):
    store = get_store(table_name=table_name)
    docs= []
    with open(doc_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            docs.append(Document(page_content=rec["page_content"], metadata=rec["metadata"]))
            print('loading')
    if not docs:
        raise ValueError(f"{doc_path}에서 문서를 읽지 못했습니다 (0건)")
    store.add_documents(docs)
    print(f"{len(docs)}건 적재 완료")

if __name__ == "__main__":
    load(table_name='foodsafety_fd_cd')