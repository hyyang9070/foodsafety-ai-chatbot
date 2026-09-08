"""data/md/*.md → data/doc.jsonl

실행: python -m rag.preprocessor
"""

from pathlib import Path
from rag.chunk import to_chunks
from rag.headers import FOOD_CODE, TEST_METHOD, mark_header
from rag.io import save_documents

# 작업 디렉터리와 무관하게 프로젝트 루트 기준으로 해석
BASE_DIR = Path(__file__).resolve().parent.parent
MD_DIR = BASE_DIR / "data" / "md"
OUT = BASE_DIR / "data" / "doc.jsonl"

def main():
    docs = []

    for path in sorted(MD_DIR.glob("*.md")):
        # 8장 -> 시험법
        is_test_method = path.name.startswith("(3-")
        rules = TEST_METHOD if is_test_method else FOOD_CODE
        marked = mark_header(path.read_text(encoding="utf-8"), rules=rules)
        chunks = to_chunks(
            marked,
            source=path.stem,
        )
        docs += chunks
        print(f"{path.stem}: {len(chunks)}청크")

    save_documents(docs, OUT)
    print(f"총 {len(docs)}청크 → {OUT}")


if __name__ == "__main__":
    main()
