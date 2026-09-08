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
- Docker Desktop (권장) 또는 PostgreSQL 및 `vector` 확장
- Anthropic API 키
- Voyage AI API 키

## 설치

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS 또는 Linux에서는 다음과 같이 가상환경을 활성화합니다.

```bash
source .venv/bin/activate
```

## 환경 변수

`backend/.env` 파일을 생성합니다. 이 파일은 Git에서 제외됩니다.

```dotenv
ANTHROPIC_API_KEY=your_anthropic_api_key
VOYAGE_API_KEY=your_voyage_api_key
```

현재 데이터베이스 연결과 모델 설정은 `core/config.py`에서 관리합니다.

```python
CONNECTION_STRING = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"
EMBEDDING_MODEL = "voyage-3-large"
CHAT_MODEL = "anthropic:claude-sonnet-4-6"
```

운영 환경에서는 연결 문자열을 환경 변수로 분리하는 것을 권장합니다.

## 로컬 데이터베이스 구성

### Docker로 동일한 환경 구성하기 (권장)

[pgvector 공식 Docker 이미지](https://github.com/pgvector/pgvector#docker)를 사용하면 현재 코드의 기본 연결값과 동일한 로컬 DB를 바로 만들 수 있습니다. Docker Desktop을 실행한 뒤 다음 명령을 입력합니다.

```powershell
docker volume create foodsafety-postgres-data
docker run --name foodsafety-postgres -e POSTGRES_USER=langchain -e POSTGRES_PASSWORD=langchain -e POSTGRES_DB=langchain -p 6024:5432 -v foodsafety-postgres-data:/var/lib/postgresql/data -d pgvector/pgvector:pg16
```

생성된 `langchain` 데이터베이스에서 `vector` 확장을 활성화합니다. 확장은 데이터베이스마다 한 번씩 활성화해야 합니다.

```powershell
docker exec foodsafety-postgres psql -U langchain -d langchain -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

현재 기본 연결 정보는 다음과 일치합니다.

| 항목 | 값 |
| --- | --- |
| Host | `localhost` |
| Port | `6024` |
| Database | `langchain` |
| User | `langchain` |
| Password | `langchain` |
| Connection string | `postgresql+psycopg://langchain:langchain@localhost:6024/langchain` |

DB 파일은 Docker의 `foodsafety-postgres-data` 볼륨에 보존됩니다.

```powershell
docker stop foodsafety-postgres
docker start foodsafety-postgres
```

컨테이너를 중지하거나 Docker Desktop을 재시작해도 볼륨을 삭제하지 않는 한 적재된 데이터는 유지됩니다.

### 기존 로컬 PostgreSQL 사용하기

이미 PostgreSQL과 pgvector가 설치되어 있다면 사용할 데이터베이스에서 다음 SQL을 실행합니다.

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

그다음 `core/config.py`의 `CONNECTION_STRING`을 실제 사용자, 비밀번호, 포트와 데이터베이스 이름에 맞게 수정합니다. pgvector 설치 자체가 필요하면 [공식 설치 안내](https://github.com/pgvector/pgvector#installation)를 참고하세요.

## 데이터 전처리 및 적재

다음 과정은 클론한 사용자의 로컬 환경에서 식품공전 검색 데이터를 새로 만드는 단계입니다. 모든 명령은 가상환경이 활성화된 `backend` 디렉터리에서 실행합니다.

```text
data/md/*.md
    ↓ python -m rag.preprocessor
data/doc.jsonl
    ↓ foodsafety_fd_cd 테이블 초기화
    ↓ python -m rag.load
Voyage AI 임베딩
    ↓
로컬 PostgreSQL의 foodsafety_fd_cd 테이블
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

`VOYAGE_API_KEY`가 `backend/.env`에 설정되어 있고 로컬 PostgreSQL이 실행 중인지 확인한 뒤 적재합니다.

```powershell
python -m rag.load
```

`rag.load`는 `data/doc.jsonl`의 각 청크를 Voyage AI로 임베딩한 후 `foodsafety_fd_cd` 테이블에 저장합니다. 문서 수에 따라 시간이 걸리고 Voyage AI API 사용량이 발생할 수 있습니다.

### 5. 적재 결과 확인

Docker 환경에서는 다음 명령을 실행합니다.

```powershell
docker exec foodsafety-postgres psql -U langchain -d langchain -c "SELECT COUNT(*) AS document_count FROM foodsafety_fd_cd;"
docker exec foodsafety-postgres psql -U langchain -d langchain -c "SELECT extversion FROM pg_extension WHERE extname = 'vector';"
```

첫 번째 결과가 `0`보다 크고 두 번째 결과에 pgvector 버전이 표시되면 준비가 완료된 것입니다.

### 재실행 시 주의사항

`python -m rag.preprocessor`는 `data/doc.jsonl`을 다시 생성하므로 반복 실행해도 됩니다. 반면 `python -m rag.load`는 기존 테이블에 문서를 추가하므로 같은 데이터를 반복해서 적재하면 중복될 수 있습니다. 데이터를 새로 구축하려면 기존 DB 또는 대상 테이블을 먼저 정리한 뒤 적재해야 합니다.

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
