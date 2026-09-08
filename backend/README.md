# Backend

식품공전 문서를 검색하고 근거 기반 답변을 생성하는 FastAPI RAG 서버입니다.

## 제공 기능

- `POST /chat` 채팅 API
- 식품공전 기준·규격 및 시험법 벡터 검색
- 검색 결과와 출처 분류 경로를 이용한 답변 생성
- `thread_id` 기반 대화 문맥 유지
- Markdown 전처리, JSONL 생성 및 pgvector 적재

## 요구 사항

- Python 3.12 이상
- Neon 프로젝트 또는 공유받은 Neon DB 접근 권한
- Anthropic API 키
- Voyage AI API 키

## 설치

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS 또는 Linux에서는 다음과 같이 가상환경을 활성화합니다.

```bash
source .venv/bin/activate
```

## 환경 변수

예제 파일을 복사해 `backend/.env`를 생성합니다. 이 파일은 Git에서 제외됩니다.

```powershell
Copy-Item .env.example .env
```

```dotenv
DATABASE_URL=postgresql://[user]:[password]@[neon-hostname]/[database]?sslmode=require&channel_binding=require
ANTHROPIC_API_KEY=your_anthropic_api_key
VOYAGE_API_KEY=your_voyage_api_key
```

Neon 콘솔의 프로젝트 화면에서 **Connect**를 눌러 연결 문자열을 복사한 뒤 `DATABASE_URL`에 입력합니다. 백엔드는 Neon의 `postgresql://` 접두사를 SQLAlchemy psycopg 3 형식으로 자동 변환합니다.

> 연결 문자열에는 DB 비밀번호가 포함됩니다. `.env`를 커밋하거나 연결 문자열을 README, 채팅 또는 이슈에 공개하지 마세요.

## Neon 데이터베이스 구성

### 1. 프로젝트 연결

다음 중 현재 상황에 맞는 방법을 선택합니다.

- 팀의 기존 DB 사용: Neon 프로젝트 초대를 받은 뒤 동일한 프로젝트, 브랜치, 데이터베이스의 연결 문자열을 사용합니다.
- 개인 DB 사용: Neon에서 새 프로젝트 또는 브랜치를 만들고 자신의 연결 문자열을 사용합니다.

테이블 초기화와 데이터 적재에는 Neon **Direct connection** 문자열을 사용하는 편이 안전합니다. 앱 실행 시 연결 수가 많다면 이후 **Pooled connection** 문자열을 사용할 수 있습니다.

### 2. pgvector 활성화

Neon 콘솔의 **SQL Editor**에서 연결할 데이터베이스를 선택하고 다음 SQL을 한 번 실행합니다.

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Neon은 pgvector 확장을 지원하며 데이터베이스마다 확장을 한 번 활성화해야 합니다. 자세한 내용은 [Neon의 pgvector 안내](https://neon.com/docs/ai/ai-concepts#storing-vector-embeddings-in-postgres)를 참고하세요.

### 3. 기존 데이터 여부 확인

팀의 Neon DB에 이미 `foodsafety_fd_cd` 테이블과 데이터가 있다면 아래 쿼리로 확인할 수 있습니다.

```sql
SELECT COUNT(*) AS document_count FROM foodsafety_fd_cd;
```

테이블이 있고 결과가 `0`보다 크면 아래의 전처리, 테이블 초기화 및 적재 단계는 건너뛰고 서버를 실행합니다.

## 데이터 전처리 및 적재

다음 과정은 비어 있는 Neon DB에 식품공전 검색 데이터를 새로 만드는 단계입니다. 모든 명령은 가상환경이 활성화된 `backend` 디렉터리에서 실행합니다.

```text
data/md/*.md
    ↓ python -m rag.preprocessor
data/doc.jsonl
    ↓ foodsafety_fd_cd 테이블 초기화
    ↓ python -m rag.load
Voyage AI 임베딩
    ↓
Neon PostgreSQL의 foodsafety_fd_cd 테이블
```

### 1. 원본 Markdown 확인

전처리 대상은 `data/md/*.md`입니다. 새 문서를 추가하려면 UTF-8 형식의 Markdown 파일을 이 디렉터리에 넣습니다.

### 2. 전처리 실행

```powershell
python -m rag.preprocessor
```

이 명령은 다음 작업을 수행합니다.

- 식품공전 제목 계층 정규화
- 문서 구조와 표를 고려한 청킹
- 청크별 출처 및 계층 메타데이터 생성
- 결과를 `data/doc.jsonl`에 저장

정상적으로 끝나면 터미널에 파일별 청크 수와 전체 청크 수가 표시됩니다. PowerShell에서는 다음 명령으로 생성 여부와 레코드 수를 확인할 수 있습니다.

```powershell
Test-Path .\data\doc.jsonl
(Get-Content .\data\doc.jsonl).Count
```

### 3. 벡터 테이블 초기화

완전히 새로 만든 DB에는 `foodsafety_fd_cd` 테이블이 없으므로 한 번만 초기화해야 합니다. 현재 임베딩 모델인 `voyage-3-large`는 기본적으로 1,024차원 벡터를 생성합니다.

```powershell
python -c "from langchain_postgres import PGEngine; from core.config import CONNECTION_STRING; engine = PGEngine.from_connection_string(url=CONNECTION_STRING); engine.init_vectorstore_table(table_name='foodsafety_fd_cd', vector_size=1024)"
```

이 명령은 LangChain `PGVectorStore`가 사용하는 `content`, `embedding`, `langchain_metadata` 등의 컬럼을 생성합니다. 이미 테이블을 초기화했다면 다시 실행하지 않습니다.

- [LangChain PostgreSQL 벡터 스토어 공식 예제](https://github.com/langchain-ai/langchain-postgres#vectorstore)
- [Voyage AI 임베딩 차원 안내](https://docs.voyageai.com/docs/embeddings)

임베딩 모델 또는 출력 차원을 변경하면 새 테이블의 `vector_size`도 같은 값으로 맞춰야 합니다.

### 4. 벡터 DB 적재

`DATABASE_URL`과 `VOYAGE_API_KEY`가 `backend/.env`에 설정되어 있는지 확인한 뒤 적재합니다.

```powershell
python -m rag.load
```

`rag.load`는 `data/doc.jsonl`의 각 청크를 Voyage AI로 임베딩한 후 `foodsafety_fd_cd` 테이블에 저장합니다. 문서 수에 따라 시간이 걸리고 Voyage AI API 사용량이 발생할 수 있습니다.

### 5. 적재 결과 확인

Neon SQL Editor에서 다음 쿼리를 실행합니다.

```sql
SELECT COUNT(*) AS document_count FROM foodsafety_fd_cd;
SELECT extversion FROM pg_extension WHERE extname = 'vector';
```

첫 번째 결과가 `0`보다 크고 두 번째 결과에 pgvector 버전이 표시되면 준비가 완료된 것입니다.

### 재실행 시 주의사항

`python -m rag.preprocessor`는 `data/doc.jsonl`을 다시 생성하므로 반복 실행해도 됩니다. 반면 `python -m rag.load`는 기존 테이블에 문서를 추가하므로 같은 데이터를 반복해서 적재하면 중복될 수 있습니다. 팀이 같은 Neon DB를 공유한다면 DB 담당자만 적재를 수행하세요. 데이터를 새로 구축하려면 기존 DB 또는 대상 테이블을 먼저 정리한 뒤 적재해야 합니다.

## 서버 실행

`backend` 디렉터리에서 실행합니다.

```powershell
uvicorn main:app --reload
```

- Swagger UI: <http://127.0.0.1:8000/docs>
- OpenAPI: <http://127.0.0.1:8000/openapi.json>

## API

### `POST /chat`

요청:

```json
{
  "message": "고춧가루의 수분 기준을 알려줘",
  "thread_id": "demo-user-1"
}
```

응답:

```json
{
  "answer": "검색된 식품공전 근거를 바탕으로 생성된 답변"
}
```

동일한 `thread_id`를 사용하면 서버가 실행되는 동안 이전 대화 문맥이 이어집니다. 현재 체크포인터는 메모리 방식이므로 서버를 재시작하면 대화가 초기화됩니다.

## 디렉터리 구조

```text
backend/
├── api/
│   ├── routes.py            # POST /chat
│   └── schemas.py           # 요청·응답 모델
├── core/
│   └── config.py            # DB, 모델, CORS 설정
├── data/
│   ├── md/                  # 식품공전 Markdown
│   └── doc.jsonl            # 전처리된 청크
├── model/
│   ├── embedding.py         # Voyage AI 임베딩
│   └── pool.py              # PostgreSQL 연결
├── rag/
│   ├── agent.py             # RAG 에이전트
│   ├── chunk.py             # 구조 인식 청킹
│   ├── headers.py           # 제목 정규화 규칙
│   ├── preprocessor.py      # Markdown → JSONL
│   ├── load.py              # JSONL → pgvector
│   └── tools.py             # 식품공전 검색 도구
└── main.py                  # FastAPI 진입점
```

## 참고 사항

- 검색 대상은 식품공전의 기준·규격과 시험법이며 개별 유통 제품 정보는 포함하지 않습니다.
- 기본 CORS 허용 주소는 `http://localhost:5173`입니다.
- 모델 답변은 참고용이며 공식적인 법적·행정적 판단을 대신하지 않습니다.
