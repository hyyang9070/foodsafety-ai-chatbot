# 식품공전 RAG 챗봇

식품위해예측 시스템 페이지의 기능 중 일부로 사용되기 위해 개발되었습니다. 
대국민 또는 식품제조 가공업자가 사용가능한 원료 기준·규격과 시험법을 자연어로 검색하고, 검색된 근거를 바탕으로 답변하는 RAG(Retrieval-Augmented Generation) 챗봇입니다.

식품공전 문서의 계층 구조와 표를 보존해 검색용 데이터로 가공하고, Postgres(pgvector)의 벡터 검색 결과를 Claude llm 에 전달합니다. FastAPI의 `/chat` API는 같은 `thread_id` 안에서 대화 문맥을 유지합니다.

> 이 프로젝트의 답변은 정보 탐색을 돕기 위한 것이며 법적·행정적 판단을 대신하지 않습니다. 실제 업무에는 최신 식품공전과 관계 기관의 공식 해석을 확인하세요.

## 주요 기능

- 식품공전 Markdown 문서의 제목 계층 자동 인식
- 표를 분리·복원해 표 내부가 잘리지 않도록 보호
- 헤더 우선 분할 후 큰 문단만 재분할하는 구조 인식 청킹
- 문서, 섹션, 청크 단위의 추적 가능한 메타데이터 생성
- Voyage AI 임베딩과 pgvector cosine distance 기반 Top-K 검색
- 검색 도구를 사용하는 Claude 기반 RAG 에이전트
- `thread_id` 기반 멀티턴 대화
- FastAPI 비동기 REST API

## 동작 구조

```text
사용자 질문
    │
    ▼
POST /chat ── thread_id 기반 대화 문맥
    │
    ▼
Claude Agent
    │ tool call
    ▼
질문 임베딩 (voyage-3-large)
    │
    ▼
PostgreSQL + pgvector
    │ cosine similarity / Top-K
    ▼
관련 식품공전 청크 + 분류 경로
    │
    ▼
근거 기반 답변
```

데이터는 다음 파이프라인으로 준비합니다.

```text
data/md/*.md
    → 헤더 정규화
    → 구조 인식 청킹 및 표 보호
    → data/doc.jsonl
    → Voyage AI 임베딩
    → PostgreSQL/pgvector
```

## 기술 스택

| 영역 | 기술 |
| --- | --- |
| API | Python 3.12, FastAPI, Uvicorn, Pydantic |
| Agent | LangChain, LangGraph |
| LLM | Anthropic Claude Sonnet 4.6 |
| Embedding | Voyage AI `voyage-3-large` |
| Vector DB | PostgreSQL, pgvector, LangChain Postgres |
| 전처리 | MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter |

## 프로젝트 구조

```text
FastAPIProject/
├── api/
│   ├── routes.py           # POST /chat 엔드포인트
│   └── schemas.py          # 요청·응답 모델
├── core/
│   └── config.py           # 모델, DB, CORS 설정
├── data/
│   ├── md/                 # 전처리 대상 식품공전 Markdown
│   └── doc.jsonl           # 생성된 청크 데이터
├── model/
│   ├── embedding.py        # Voyage AI 임베딩
│   └── pool.py             # SQLAlchemy/PGEngine 생성
├── rag/
│   ├── agent.py            # RAG 에이전트와 시스템 프롬프트
│   ├── chunk.py            # 구조 인식 청킹
│   ├── headers.py          # 식품공전 헤더 정규화 규칙
│   ├── preprocessor.py     # Markdown → JSONL
│   ├── load.py             # JSONL → Vector DB
│   ├── store.py            # PGVectorStore 구성
│   └── tools.py            # 식품공전 벡터 검색 도구
├── sql/                    # DB 구성·실험용 SQL
├── main.py                 # FastAPI 애플리케이션 진입점
├── requirements.txt
└── test_main.http          # API 호출 예시
```

## 시작하기

### 1. 요구 사항

- Python 3.12 이상
- PostgreSQL과 `vector` 확장
- Anthropic API Key
- Voyage AI API Key

### 2. 설치

```bash
git clone <repository-url>
cd FastAPIProject

python -m venv .venv
```

가상 환경을 활성화합니다.

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

```bash
pip install -r requir# 식품공전 기반 RAG AI 챗봇

> **대국민 식품위해예측 서비스 활용을 위한 식품안전 전문 RAG(Retrieval-Augmented Generation) 질의응답 시스템**

## 1. 프로젝트 개요

본 프로젝트는 **회사 업무의 일환으로 수행한 RAG 기반 AI 서비스 개발 프로젝트**입니다.

식품공전에는 식품의 기준·규격, 원료 기준, 시험법, 잔류농약 및 동물용의약품 허용기준 등 방대한 식품안전 정보가 포함되어 있습니다.

그러나 전문 용어가 많고 문서 구조가 복잡하여 일반 사용자가 원하는 정보를 직접 검색하고 정확한 근거를 찾는 데 어려움이 있습니다.

이를 개선하기 위해 식품공전 문서를 RAG에 활용할 수 있는 형태로 구조화하고, 사용자의 자연어 질문과 관련된 문서를 검색하여 해당 내용을 근거로 답변하는 **RAG 기반 식품공전 AI 챗봇**을 개발했습니다.

향후 본 시스템은 **대국민 식품위해예측 서비스의 식품안전 정보 탐색 및 자연어 질의응답 기능**으로 활용하는 것을 목표로 합니다.

---

# 2. 프로젝트 목표

기존의 키워드 중심 검색 방식에서 벗어나 사용자가 자연어로 질문하면 관련 식품공전 내용을 검색하고 근거 기반 답변을 제공할 수 있는 시스템 구축을 목표로 했습니다.

```text
사용자 자연어 질문
        ↓
관련 식품공전 검색
        ↓
관련 근거 문서 추출
        ↓
LLM Context 구성
        ↓
근거 기반 답변 생성
```

핵심 목표는 LLM 자체 지식에 의존하는 챗봇이 아니라 **공식 식품안전 데이터를 Knowledge Base로 활용하는 RAG 시스템을 구축하는 것**입니다.

---

# 3. 담당 업무

본 프로젝트에서 **식품공전 데이터 전처리부터 RAG 검색 Pipeline 구축까지의 개발 업무**를 수행했습니다.

주요 담당 영역은 다음과 같습니다.

* 식품공전 데이터 구조 분석
* HWPX 문서 Parsing 및 데이터 전처리
* Markdown / JSONL 데이터 구축
* 문서 Chunking 전략 설계 및 구현
* Chunk Metadata 구성
* Embedding 기반 Vector Search 구축
* Vector Index 구성
* RAG Retrieval Pipeline 개발
* FastAPI 기반 질의응답 API 개발
* 검색 결과와 LLM을 연결하는 Context 구성
* 검색 및 답변 품질 개선

---

# 4. 전체 RAG 구조

```text
                     User
                       │
                Natural Language
                    Question
                       │
                       ▼
                   FastAPI
                       │
                       ▼
                Query Processing
                       │
                       ▼
                Query Embedding
                       │
                       ▼
             ┌──────────────────┐
             │    Vector DB     │
             │    HNSW Index    │
             └────────┬─────────┘
                      │
               Similarity Search
                      │
                      ▼
             Relevant Documents
                      │
                      ▼
                 Top-K Context
                      │
                      ▼
              Question + Context
                      │
                      ▼
                     LLM
                      │
                      ▼
              Generated Answer
```

---

# 5. 데이터 처리 Pipeline

식품공전 원본 문서를 다음 과정으로 처리하여 RAG Knowledge Base를 구축했습니다.

```text
식품공전 HWPX
      ↓
Text / Table Parsing
      ↓
Noise Removal
      ↓
Markdown Normalization
      ↓
Document Structure Analysis
      ↓
Document Chunking
      ↓
Metadata Mapping
      ↓
JSONL
      ↓
Embedding
      ↓
Vector DB
      ↓
HNSW Index
```

식품공전은 표와 계층적인 문서 구조가 많기 때문에 단순 Text Extraction보다는 **원본 문서의 의미와 구조를 최대한 보존하는 것**을 중요하게 고려했습니다.

---

# 6. 현재까지 수행 완료한 개발

> 아래 항목은 프로젝트에서 **실제로 개발 및 적용을 완료한 영역**입니다.

## 6.1 식품공전 HWPX Parsing

식품공전 원본 HWPX 문서를 RAG 시스템에서 사용할 수 있는 데이터 형태로 변환했습니다.

### 수행 내용

* HWPX 문서 텍스트 추출
* 문서 내 Table 데이터 추출
* 불필요한 데이터 및 노이즈 제거
* Markdown 형식 변환
* Markdown 정규화
* 문서 제목 및 문단 구조 보존

특히 식품공전의 기준·규격 및 시험법은 표 형태의 데이터가 많기 때문에 **Table 구조가 최대한 손실되지 않도록 데이터 변환을 수행했습니다.**

---

## 6.2 식품공전 데이터 구조화

Parsing된 데이터를 RAG Pipeline에서 활용할 수 있도록 구조화했습니다.

```text
HWPX
 ↓
Markdown
 ↓
Document Cleaning
 ↓
JSONL
 ↓
RAG Document
```

문서 본문뿐 아니라 검색 결과의 출처를 추적할 수 있도록 Metadata를 함께 관리하도록 구성했습니다.

---

## 6.3 Document Chunking

식품공전 문서를 검색 가능한 단위로 분할하는 Chunking 로직을 구현했습니다.

단순하게 일정 글자 수만을 기준으로 분할하는 방식보다 **식품공전 문서의 의미 단위와 구조를 최대한 유지하는 방향**으로 Chunk를 구성했습니다.

```text
Food Code Document

├── Chapter
├── Section
├── Paragraph
└── Table
       ↓
    Chunk
```

Chunk 경계에서 문맥이 손실되는 문제를 줄이기 위해 **Chunk Overlap**도 적용했습니다.

```text
Chunk 1
[-----------------------]
                 [------]
                        Chunk 2
                        [-----------------------]
```

---

## 6.4 Metadata 구성

각 Chunk가 원본 식품공전의 어느 문서에서 생성되었는지 추적할 수 있도록 Metadata를 구성했습니다.

예를 들어 다음과 같은 참조 정보를 Chunk와 함께 관리합니다.

```text
content
source
document
author
created_at
```

이를 통해 검색된 Chunk의 원본 출처를 확인하고 향후 답변에 출처 정보를 연결할 수 있는 기반을 마련했습니다.

---

## 6.5 Embedding 기반 검색 구축

Chunking된 식품공전 데이터를 Embedding하여 의미 기반 검색이 가능하도록 구성했습니다.

```text
Document
   ↓
Embedding Model
   ↓
Vector
   ↓
Vector DB
```

사용자 질문 역시 Embedding하여 문서 Vector와의 의미적 유사도를 기반으로 관련 문서를 검색합니다.

---

## 6.6 HNSW Vector Index 구축

Vector 검색 성능 향상을 위해 **HNSW 기반 Index**를 구성했습니다.

```text
User Query
     ↓
Query Embedding
     ↓
HNSW Index
     ↓
Similarity Search
     ↓
Top-K Documents
```

이를 통해 사용자의 질문과 의미적으로 유사한 식품공전 Chunk를 검색할 수 있는 Retrieval 구조를 구축했습니다.

---

## 6.7 RAG Retrieval Pipeline 구축

사용자 질문을 입력받아 관련 식품공전 문서를 검색하고 LLM에 전달하는 기본 RAG Pipeline을 구축했습니다.

```text
User Question
      ↓
Query Embedding
      ↓
Vector Search
      ↓
Top-K Retrieval
      ↓
Context 구성
      ↓
LLM
      ↓
Answer
```

LLM 자체 지식만으로 답변하지 않고 **검색된 식품공전 내용을 Context로 활용하여 답변하도록 구성했습니다.**

---

## 6.8 FastAPI 기반 API 구축

RAG Pipeline을 서비스에서 활용할 수 있도록 FastAPI 기반 질의응답 API를 구현했습니다.

```text
Client

POST /query
     ↓
FastAPI
     ↓
RAG Pipeline
     ↓
Retriever
     ↓
LLM
     ↓
Response
```

이를 통해 향후 대국민 식품위해예측 서비스의 사용자 인터페이스와 RAG 시스템을 연결할 수 있는 기반을 마련했습니다.

---

# 7. 현재 구축한 Knowledge Base

현재 **식품공전 「식품의 기준 및 규격」**을 중심으로 RAG Knowledge Base를 구축했습니다.

현재 처리 대상에는 다음 데이터가 포함됩니다.

* 제1장 ~ 제5장
* 제6장 ~ 제7장
* 제8장 시험법
* 미생물 시험법
* 식품 중 잔류농약 시험법
* 식품 중 잔류동물용의약품 시험법
* 유해물질 시험법
* 제9장 재검토기한
* 식품 원료 목록
* 농약 잔류허용기준
* 동물용의약품 잔류허용기준
* 잔류허용기준 설정이 필요 없는 물질

식품공전 데이터를 검색 가능한 Chunk 형태로 가공하여 Vector DB에서 활용할 수 있도록 구축했습니다.

---

# 8. 향후 RAG 고도화 계획

> 아래 항목은 현재 구현 완료된 기능이 아니라 **향후 개발 및 성능 고도화를 위해 계획하고 있는 영역**입니다.

현재 구축한 기본 RAG Pipeline을 다음과 같은 구조로 확장하는 것을 목표로 합니다.

```text
                  User Query
                       │
                       ▼
                Query Rewriting
                       │
                       ▼
              Query Decomposition
                       │
            ┌──────────┴──────────┐
            ▼                     ▼
      Dense Retrieval       Sparse Retrieval
      Vector Search              BM25
            │                     │
            └──────────┬──────────┘
                       ▼
                 RRF Fusion
                       │
                       ▼
                   Reranker
                       │
                       ▼
              Optimized Context
                       │
                       ▼
                      LLM
                       │
                       ▼
             Answer + Citation
```

---

## 8.1 Query Rewriting

사용자가 입력한 자연어 질문이 항상 검색에 최적화되어 있지는 않기 때문에 LLM을 이용하여 질문을 검색에 적합한 형태로 변환하는 기능을 추가할 예정입니다.

```text
Original Query
      ↓
LLM Query Rewriting
      ↓
Search Optimized Query
      ↓
Retriever
```

특히 일반 사용자가 전문적인 식품공전 용어를 알지 못하는 경우에도 관련 전문 용어와 연결될 수 있도록 검색 성능을 개선하는 것이 목표입니다.

---

## 8.2 Query Decomposition

하나의 질문에 여러 조건이 포함된 **복합 질문 및 Multi-hop Query** 처리를 개선할 예정입니다.

```text
Complex Question
       ↓
Query Decomposition
       ↓
 ┌─────┼─────┐
 ▼     ▼     ▼
Q1    Q2     Q3
 │     │     │
 └─────┼─────┘
       ↓
Evidence Aggregation
```

질문을 여러 Sub-query로 분해하여 각각 필요한 근거를 검색한 뒤 최종 답변에 활용하는 구조를 검토하고 있습니다.

---

## 8.3 Hybrid Search

현재의 Dense Vector Retrieval을 확장하여 **Dense + Sparse Retrieval을 결합한 Hybrid Search**를 적용할 예정입니다.

### Dense Retrieval

Embedding을 이용하여 문장의 의미적 유사성을 검색합니다.

### Sparse Retrieval

BM25 기반 검색을 적용하여 정확한 식품명, 물질명, 시험법, 조항 번호 등 **Keyword Matching이 중요한 Query**를 보완합니다.

```text
Dense Retrieval ───────┐
                       │
                       ├── RRF
                       │
Sparse Retrieval ──────┘
                       ↓
                Candidate Documents
```

---

## 8.4 RRF 적용

Dense Search와 Sparse Search 결과를 효과적으로 결합하기 위해 **RRF(Reciprocal Rank Fusion)** 적용을 계획하고 있습니다.

이를 통해 서로 다른 검색 방식에서 높은 순위를 받은 문서를 통합하여 최종 Candidate를 구성할 예정입니다.

---

## 8.5 Reranking

Retriever에서 검색된 Candidate 문서 중 실제 사용자 질문과 관련성이 높은 문서를 다시 평가하는 **Reranking 단계**를 추가할 예정입니다.

```text
Retriever

Top-N Candidates
       ↓
Reranker
       ↓
Top-K Documents
       ↓
LLM Context
```

이를 통해 LLM에 전달되는 불필요한 Context를 줄이고 관련성이 높은 근거 문서를 우선적으로 제공하는 것을 목표로 합니다.

---

## 8.6 Structure-aware Retrieval

현재의 Chunk 단위 검색에서 나아가 식품공전의 계층 구조를 활용하는 검색 방식을 검토하고 있습니다.

```text
Document
 └── Chapter
      └── Section
           └── Subsection
                └── Chunk
```

검색된 Chunk뿐만 아니라 상위 조항 및 인접 Chunk의 정보를 활용하여 **문맥이 단절되는 문제를 개선하는 것**을 목표로 합니다.

---

## 8.7 Domain-specific Embedding 고도화

식품공전에는 일반 문서에서 자주 사용되지 않는 식품·화학·미생물·시험법 관련 전문 용어가 다수 존재합니다.

따라서 향후 실제 식품안전 Query-Document Pair를 확보하여 **식품안전 도메인에 특화된 Embedding 모델 Fine-tuning**을 검토할 예정입니다.

---

# 9. RAG Evaluation 체계 구축 계획

향후에는 RAG 성능을 경험적으로 판단하는 방식에서 벗어나 **정량적인 평가 Pipeline**을 구축할 예정입니다.

## Retrieval 평가

다음 지표를 활용하여 검색 성능을 평가할 계획입니다.

| Metric            | 평가 목적                       |
| ----------------- | --------------------------- |
| Context Precision | 검색 결과 중 실제 관련 문서의 비율        |
| Context Recall    | 필요한 근거 문서를 충분히 검색했는지 평가     |
| MRR               | 정답 문서가 얼마나 상위에 검색되는지 평가     |
| F1-score          | Precision과 Recall을 종합적으로 평가 |

## Generation 평가

RAGAS 등의 평가 Framework를 활용하여 다음 항목을 평가할 계획입니다.

| Metric           | 평가 목적                    |
| ---------------- | ------------------------ |
| Faithfulness     | 답변이 검색 Context에 근거하는지 평가 |
| Answer Relevance | 답변이 사용자 질문과 관련 있는지 평가    |

---

# 10. Retrieval Parameter 최적화 계획

Evaluation Dataset을 구축한 후 평가 결과를 기반으로 RAG 주요 Parameter를 조정할 예정입니다.

```text
Chunk Size
Chunk Overlap
Top-K
Similarity Threshold
Dense / Sparse Weight
RRF Parameter
Reranking Candidate Size
Final Context Size
```

즉, 특정 값을 경험적으로 선택하는 것이 아니라 **동일한 평가 데이터에 대해 실험하고 정량적인 성능 지표를 비교하여 최적값을 선정하는 구조**를 목표로 합니다.

---

# 11. Hallucination 개선 계획

대국민 식품안전 서비스에서는 잘못된 정보를 생성하지 않는 것이 중요하기 때문에 **Hallucination 최소화**를 주요 고도화 목표로 설정했습니다.

향후 다음과 같은 방법을 적용할 계획입니다.

* 검색 Context 범위 내 답변을 유도하는 Prompt 설계
* LLM Temperature 등 Generation Parameter 최적화
* 검색 근거가 부족한 경우 답변 생성 제한
* 모호한 질문에 대한 추가 정보 요청
* 답변에 식품공전 출처 및 조항 연결
* Hallucination 발생 Case 수집 및 분석

근거가 충분하지 않은 경우 임의의 답변을 생성하기보다는 다음과 같은 방식으로 처리하는 것을 목표로 합니다.

```text
검색된 식품공전 자료만으로는
해당 질문에 대한 충분한 근거를 확인하기 어렵습니다.
```

---

# 12. Knowledge Base 확장 계획

현재 **식품공전**을 중심으로 구축된 Knowledge Base를 향후 식품안전 관련 공식 데이터로 확대할 예정입니다.

### 공전 데이터

* 식품공전 — **현재 구축**
* 건강기능식품공전 — 향후 확장
* 식품첨가물공전 — 향후 확장
* 기구 및 용기·포장 공전 — 향후 확장

### 식품안전 관련 데이터

향후 다음과 같은 데이터를 단계적으로 검토할 예정입니다.

* 잔류농약 정보 및 허용기준
* 동물용의약품 정보 및 잔류허용기준
* 식품 원재료 정보
* 방사능 조사 관련 정보
* 축산물 기준 및 규격
* 식품안전 관련 법령 및 제도 데이터

궁극적으로 여러 식품안전 데이터 소스를 연결한 **통합 Food Safety Knowledge Base** 구축을 목표로 합니다.

---

# 13. Knowledge Base 자동 동기화 계획

식품공전과 관련 기준은 지속적으로 개정되므로 운영 환경에서는 Knowledge Base의 최신성을 유지하는 것이 중요합니다.

향후 데이터 변경을 탐지하여 Vector DB까지 반영할 수 있는 자동화 Pipeline 구축을 계획하고 있습니다.

```text
Official Data Source
        ↓
변경 데이터 확인
        ↓
신규 / 수정 데이터 탐지
        ↓
Parsing
        ↓
Chunking
        ↓
Embedding
        ↓
Vector DB Update
```

이를 통해 최신 식품안전 데이터를 지속적으로 반영할 수 있는 Knowledge Base 운영 구조로 확장하는 것이 목표입니다.

---

# 14. 개발 단계

## Phase 1 — 기본 RAG 구축 ✅

```text
HWPX Parsing
      ↓
Data Cleaning
      ↓
Markdown / JSONL
      ↓
Document Chunking
      ↓
Metadata
      ↓
Embedding
      ↓
HNSW Vector Search
      ↓
RAG Pipeline
      ↓
FastAPI
```

**현재까지 수행한 영역입니다.**

## Phase 2 — Retrieval 고도화 📌

```text
Query Rewriting
      ↓
Query Decomposition
      ↓
Dense + BM25
      ↓
RRF
      ↓
Reranking
      ↓
Context Optimization
```

**향후 개발 예정 영역입니다.**

## Phase 3 — 평가 및 품질 개선 📌

```text
Evaluation Dataset
      ↓
Retrieval Evaluation
      ↓
RAGAS
      ↓
Parameter Optimization
      ↓
Hallucination Analysis
```

## Phase 4 — Knowledge Base 확장 및 운영 📌

```text
Additional Food Safety Data
      ↓
Automated Data Synchronization
      ↓
Vector DB Update
      ↓
Knowledge Base Management
```

---

# 15. 개발 현황

| 구분             | 개발 항목                              | 상태    |
| -------------- | ---------------------------------- | ----- |
| Data           | HWPX 문서 Parsing                    | ✅ 완료  |
| Data           | Table 구조 추출 및 보존                   | ✅ 완료  |
| Data           | Noise 제거 / Markdown 정규화            | ✅ 완료  |
| Data           | JSONL 데이터 구축                       | ✅ 완료  |
| Chunking       | 문서 Chunking                        | ✅ 완료  |
| Chunking       | Chunk Overlap                      | ✅ 완료  |
| Metadata       | 기본 Reference Metadata              | ✅ 완료  |
| Embedding      | 문서 Embedding                       | ✅ 완료  |
| Retrieval      | HNSW Vector Index                  | ✅ 완료  |
| Retrieval      | Vector Similarity Search           | ✅ 완료  |
| RAG            | Retrieval → Context → LLM Pipeline | ✅ 완료  |
| API            | FastAPI 기반 RAG API                 | ✅ 완료  |
| Query          | Query Rewriting                    | 📌 예정 |
| Query          | Query Decomposition                | 📌 예정 |
| Retrieval      | BM25                               | 📌 예정 |
| Retrieval      | Hybrid Search                      | 📌 예정 |
| Retrieval      | RRF                                | 📌 예정 |
| Retrieval      | Reranking                          | 📌 예정 |
| Retrieval      | Structure-aware Retrieval          | 📌 예정 |
| Embedding      | Domain Fine-tuning                 | 📌 검토 |
| Evaluation     | Evaluation Dataset 구축              | 📌 예정 |
| Evaluation     | RAGAS                              | 📌 예정 |
| Evaluation     | MRR / Precision / Recall / F1      | 📌 예정 |
| Generation     | Hallucination 개선                   | 📌 예정 |
| Knowledge Base | 추가 식품안전 데이터 확장                     | 📌 예정 |
| Knowledge Base | 데이터 자동 동기화                         | 📌 예정 |

**범례:** ✅ 수행 완료 · 📌 향후 개발/검토

---

# 16. 최종 RAG 고도화 목표

```text
                    User Query
                         │
                         ▼
                Query Transformation
                         │
                         ▼
          ┌──────────────┴──────────────┐
          ▼                             ▼
   Dense Retrieval               Sparse Retrieval
    Vector Search                     BM25
          │                             │
          └──────────────┬──────────────┘
                         ▼
                    RRF Fusion
                         │
                         ▼
                     Reranker
                         │
                         ▼
              Structure-aware Context
                         │
                         ▼
                        LLM
                         │
                         ▼
              Grounded Answer + Source
                         │
                         ▼
                  RAG Evaluation
                         │
                         ▼
              Continuous Improvement
```

현재 구축한 **식품공전 Vector Search 기반 RAG 시스템**을 기반으로 Retrieval 정확도, 답변 신뢰성, 평가 체계 및 Knowledge Base 운영 자동화를 단계적으로 고도화하여 **대국민 식품위해예측 서비스에서 활용할 수 있는 식품안전 전문 RAG 시스템**으로 발전시키는 것을 목표로 합니다.

---

# 17. Disclaimer

본 프로젝트는 **회사에서 수행한 RAG 개발 업무 및 기술적 경험을 정리한 Repository**입니다.

README에서 `수행 완료`로 표시된 항목은 실제 프로젝트에서 개발한 내용을 의미하며, `향후 개발`, `예정`, `검토`로 표시된 항목은 서비스 고도화를 위해 계획하거나 기술적으로 검토하고 있는 내용입니다.

보안 및 기밀 유지를 위해 실제 운영 환경의 일부 코드, 데이터, API 정보, 모델 설정, 인프라 구성 및 내부 업무 정보는 공개하지 않거나 일반화하여 기술할 수 있습니다.

본 Repository의 Architecture 및 Roadmap은 기술적인 개발 방향을 설명하기 위한 것으로 실제 운영 서비스의 전체 시스템 구성을 의미하지 않습니다.
ements.txt
```

### 3. 환경 변수

프로젝트 루트에 `.env` 파일을 생성합니다. `.env`는 Git에 포함되지 않습니다.

```dotenv
ANTHROPIC_API_KEY=your_anthropic_api_key
VOYAGE_API_KEY=your_voyage_api_key
```

현재 DB 연결 정보와 모델명은 `core/config.py`에서 관리합니다.

```python
CONNECTION_STRING = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"
EMBEDDING_MODEL = "voyage-3-large"
CHAT_MODEL = "anthropic:claude-sonnet-4-6"
```

로컬 환경에 맞게 `CONNECTION_STRING`을 변경하세요. 운영 환경에서는 연결 문자열도 환경 변수로 분리하는 것을 권장합니다.

### 4. 데이터베이스 준비

PostgreSQL 데이터베이스에서 pgvector 확장을 활성화합니다.

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

애플리케이션의 검색 대상 테이블명은 `foodsafety_fd_cd`입니다. 테이블은 LangChain `PGVectorStore` 호환 스키마여야 하며, 임베딩 차원은 사용하는 Voyage 모델의 출력 차원과 일치해야 합니다.

기존 DB를 사용한다면 다음 컬럼이 검색 쿼리에서 사용되는지 확인하세요.

```text
foodsafety_fd_cd
├── content
├── embedding
└── langchain_metadata (json/jsonb; lv1 ... lv7 포함)
```

### 5. 문서 전처리 및 적재

`data/md`의 Markdown 문서를 정규화하고 청크 JSONL을 만듭니다.

```bash
python -m rag.preprocessor
```

생성된 `data/doc.jsonl`을 Vector DB에 적재합니다. 이 과정에서 Voyage API가 호출되므로 API Key와 DB 연결을 먼저 확인하세요.

```bash
python -m rag.load
```

재실행하면 동일 문서가 중복 적재될 수 있습니다. 기존 데이터를 갱신할 때는 대상 테이블의 데이터 관리 정책을 먼저 정한 뒤 실행하세요.

### 6. API 실행

```bash
uvicorn main:app --reload
```

- API 문서: <http://127.0.0.1:8000/docs>
- OpenAPI 스키마: <http://127.0.0.1:8000/openapi.json>

## API 사용법

### `POST /chat`

요청:

```json
{
  "message": "아이스크림의 정의는 무엇인가요?",
  "thread_id": "demo-user-1"
}
```

응답:

```json
{
  "answer": "검색된 식품공전 근거를 바탕으로 생성된 답변"
}
```

cURL 예시:

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"곡류의 하위 범주는?","thread_id":"demo-1"}'
```

후속 질문에서도 같은 `thread_id`를 사용하면 이전 대화가 이어집니다. `thread_id`를 생략하면 기본값 `default`가 사용되므로, 다중 사용자 환경에서는 사용자 또는 세션별 고유 값을 전달해야 합니다.

## 전처리 방식

문서 헤더는 식품공전 본문과 시험법에 서로 다른 규칙을 적용해 `lv1`부터 `lv7`까지 정규화합니다. 이후 다음 원칙으로 청크를 생성합니다.

- Markdown 헤더 단위로 먼저 분할
- 1,500자를 넘는 섹션만 재귀적으로 분할
- 분할 청크 사이 150자 overlap 적용
- `<table>...</table>` 블록을 임시 치환한 뒤 복원해 표 분절 방지
- 원본 문서 ID, 파일, 문서 종류, 섹션 경로, 청크 해시 저장

메타데이터 예시:

```json
{
  "lv1": "제8. 일반시험법",
  "lv2": "1. 일반성분시험법",
  "src": "원본 문서명",
  "doc": {
    "id": "sha256...",
    "title": "원본 문서명",
    "src_file": "data/md/example.md",
    "type": "test_method"
  },
  "chunk": {
    "idx": 0,
    "chars": 1240,
    "hash": "sha256...",
    "splitter": "markdown_header+recursive_character",
    "max_chars": 1500,
    "overlap": 150,
    "section_path": "제8. 일반시험법 > 1. 일반성분시험법"
  }
}
```

## 현재 데이터 범위

저장소에는 식품의 기준 및 규격을 중심으로 다음 자료가 포함되어 있습니다.

- 제1장~제7장
- 제8장 일반시험법(미생물, 잔류농약, 잔류동물용의약품, 유해물질 등)
- 제9장 재검토기한
- 식품 원료 목록
- 농약 및 동물용의약품 잔류허용기준
- 잔류허용기준 설정이 필요 없는 물질

## 제한 사항 및 개선 과제

- 검색은 현재 Dense Vector Search만 사용합니다.
- 에이전트 체크포인트가 인메모리 방식이므로 서버 재시작 시 대화가 사라집니다.
- 인증, 요청 제한, 영속 세션 저장소는 아직 구현되어 있지 않습니다.
- DB 연결 문자열과 모델 설정이 코드에 고정되어 있습니다.
- 검색 품질을 정량적으로 확인하는 평가 데이터셋과 자동 평가가 필요합니다.

향후 Hybrid Search(BM25 + Dense), reranking, query rewriting/decomposition, 답변 인용 강화, 영속 체크포인트, 검색·생성 품질 평가를 적용할 수 있습니다.

## 라이선스 및 데이터 출처

별도의 라이선스 파일은 현재 포함되어 있지 않습니다. 저장소를 공개하거나 재사용하기 전에 코드 라이선스와 원문 데이터의 이용 조건을 확인하고 명시하세요.
#   f o o d s a f e t y - a i - c h a t b o t  
 