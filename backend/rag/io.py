"""청크 jsonl 저장·읽기."""

import json
from pathlib import Path

from langchain_core.documents import Document


def save_documents(docs: list[Document], path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(
                {"page_content": d.page_content, "metadata": d.metadata},
                ensure_ascii=False) + "\n")


def load_documents(path: str) -> list[Document]:
    with open(path, encoding="utf-8") as f:
        return [Document(page_content=r["page_content"], metadata=r["metadata"])
                for r in map(json.loads, f)]
