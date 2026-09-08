"""마크다운 헤더 정규화."""

import re

# (레벨, 번호패턴, 제목 최대길이) — 위에서부터 먼저 맞는 규칙을 쓴다
FOOD_CODE = [
    (1, r"제\d+\.", 50),                       # 제1. 총 칙
    (2, r"\d+\.", 40),                         # 1. 과자류, 빵류 또는 떡류
    (3, r"\d+-\d+\.?", 50),                     # 2-1 아이스크림류
    (4, r"\d+\)", 40),                         # 1) 정의
]

TEST_METHOD = [
    (1, r"제\d+\.", 50),                       # 제8. 일반시험법
    (6, r"\d+\.\d+\.\d+\.\d+\.?", 40),
    (5, r"\d+\.\d+\.\d+", 40),
    (4, r"\d+\.\d+", 40),
    (2, r"\d+\.", 40),
    (3, r"\d+\)", 40),
    (7, r"[가-힣]\.", 40),                     # 가. 나. 다.
]


def _mark(line: str, rules) -> str:
    """헤더면 '# ...', 아니면 원래 줄."""
    s = re.sub(r"^(?:#+\s*|-\s+)", "", line.strip())   # 기존 마킹은 벗기고 다시 판정

    if not s or s[0] in "|!<>":        # 표, 이미지 줄은 본문 문장
        return line
    if s.endswith("."):                # 마침표로 끝나면 본문 문장
        return line

    for level, num_pat, max_len in rules:
        m = re.match(rf"^({num_pat})\s*(\S.*)$", s)
        if not m:
            continue
        num, title = m.group(1), m.group(2)
        if title[0].isdigit() or title[0] in ".,)":
            return line                # "0.1 N 수산화나트륨액" 같은 수치·소수점
        if len(title) > max_len:       # 길면 본문 문장
            return line
        if level == 1 and re.search(r"\d", title):
            return line                # "제8. 일반시험법 3.4 ..." 같은 본문 인용
        return f"{'#' * level} {num} {title}"
    return line


def mark_header(md: str, rules=None) -> str:
    if rules is None:
        rules = FOOD_CODE
    md = re.sub(r"^제 ?\d+\n+.+\n", "", md, flags=re.M)   # 표제지 제목 제거
    return "\n".join(_mark(l, rules) for l in md.split("\n"))