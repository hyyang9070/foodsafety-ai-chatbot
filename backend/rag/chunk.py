"""마크다운을 벡터 검색용 문서로 분할한다."""

import html
import re

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

HEADERS = [
    ("#", "lv1"),
    ("##", "lv2"),
    ("###", "lv3"),
    ("####", "lv4"),
    ("#####", "lv5"),
    ("######", "lv6"),
    ("#######", "lv7"),
]

_TABLE_PATTERN = re.compile(r"<table\b[^>]*>.*?</table>", re.IGNORECASE | re.DOTALL)
_ROW_PATTERN = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.IGNORECASE | re.DOTALL)
_CELL_PATTERN = re.compile(
    r"<(th|td)\b[^>]*>(.*?)</\1>",
    re.IGNORECASE | re.DOTALL,
)
_TABLE_TOKEN = re.compile(r"@@TABLE_(\d+)@@")
_APPENDIX_HEADER_PATTERN = re.compile(r"^##\s+(\[별표\s*\d+\].*)$", re.MULTILINE)


def _normalize_appendix_headers(md: str) -> str:
    return _APPENDIX_HEADER_PATTERN.sub(r"# \1", md)


def _stash_tables(md: str) -> tuple[str, list[str]]:
    tables: list[str] = []

    def replace(match: re.Match) -> str:
        tables.append(match.group(0))
        return f"\n\n@@TABLE_{len(tables) - 1}@@\n\n"

    return _TABLE_PATTERN.sub(replace, md), tables


def _clean_cell(value: str) -> str:
    value = re.sub(r"<br\s*/?>", ", ", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", " ", value)
    return " ".join(html.unescape(value).split())


def _table_rows(table: str, section_path: str) -> list[str]:
    headers: list[str] = []
    documents: list[str] = []

    for row in _ROW_PATTERN.findall(table):
        cells = [
            (tag.lower(), _clean_cell(value))
            for tag, value in _CELL_PATTERN.findall(row)
        ]
        if not cells:
            continue

        if all(tag == "th" for tag, _ in cells):
            headers = [value for _, value in cells]
            continue

        values = [value for _, value in cells if value]
        if not values:
            continue

        lines = [f"분류: {section_path}"] if section_path else []
        if headers and len(values) == len(headers):
            lines.extend(f"{name}: {value}" for name, value in zip(headers, values))
        else:
            lines.append(" | ".join(values))
        documents.append("\n".join(lines))

    return documents


def to_chunks(
    md: str,
    source: str,
    chunk_size: int = 1500,
    chunk_overlap: int = 150,
) -> list[Document]:
    md = _normalize_appendix_headers(md)
    protected, tables = _stash_tables(md)
    header_chunks = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS,
        strip_headers=False,
    ).split_text(protected)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    documents: list[Document] = []
    for header_chunk in header_chunks:
        section = {
            key: header_chunk.metadata[key]
            for _, key in HEADERS
            if key in header_chunk.metadata
        }
        metadata = {**section, "src": source}
        section_path = " > ".join(section.values())
        parts = _TABLE_TOKEN.split(header_chunk.page_content)

        for index, part in enumerate(parts):
            if index % 2:
                row_texts = _table_rows(tables[int(part)], section_path)
                documents.extend(
                    Document(page_content=text, metadata=metadata)
                    for text in row_texts
                )
                continue

            if part.strip():
                documents.extend(
                    Document(page_content=text, metadata=metadata)
                    for text in splitter.split_text(part)
                )

    return documents
