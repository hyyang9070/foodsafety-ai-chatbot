# Frontend

식품공전 RAG API와 통신하는 React 기반 채팅 위젯입니다.

## 주요 기능

- 플로팅 버튼을 이용한 채팅창 열기와 닫기
- 사용자 질문과 챗봇 답변을 대화형 UI로 표시
- Enter 키 또는 전송 버튼을 이용한 메시지 전송
- 응답 대기 애니메이션과 오류 메시지
- 채팅 패널 크기 조절
- 홈, 대화, 설정 탭 UI

## 기술 스택

- React 19
- Vite 8
- JavaScript ES Modules
- Lucide React
- ESLint 및 Prettier

## 처음부터 실행하기

아래 순서대로 저장소를 클론한 뒤 백엔드와 프런트엔드를 각각 실행합니다.

### 사전 준비

실행 전에 다음 프로그램과 계정이 필요합니다.

- Git
- Python 3.12 이상
- Node.js와 npm
- Docker Desktop (권장) 또는 PostgreSQL 및 pgvector 확장
- Anthropic API 키
- Voyage AI API 키

### 1. 저장소 클론

```powershell
git clone https://github.com/hyyang9070/foodsafety-ai-chatbot.git
cd foodsafety-ai-chatbot
```

### 2. 백엔드 설치

프로젝트 루트에서 `backend` 디렉터리로 이동하고 Python 가상환경을 만듭니다.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

macOS 또는 Linux에서는 다음 명령으로 가상환경을 활성화합니다.

```bash
source .venv/bin/activate
```

### 3. 백엔드 환경 변수 설정

`backend/.env` 파일을 생성하고 다음 값을 입력합니다.

```dotenv
ANTHROPIC_API_KEY=your_anthropic_api_key
VOYAGE_API_KEY=your_voyage_api_key
```

`.env`는 비밀 정보가 포함되므로 Git에 커밋하지 않습니다.

### 4. 로컬 PostgreSQL 및 pgvector 준비

Docker Desktop을 실행한 뒤 다음 명령으로 현재 백엔드 설정과 동일한 로컬 DB를 만듭니다.

```powershell
docker volume create foodsafety-postgres-data
docker run --name foodsafety-postgres -e POSTGRES_USER=langchain -e POSTGRES_PASSWORD=langchain -e POSTGRES_DB=langchain -p 6024:5432 -v foodsafety-postgres-data:/var/lib/postgresql/data -d pgvector/pgvector:pg16
docker exec foodsafety-postgres psql -U langchain -d langchain -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

데이터는 `foodsafety-postgres-data` 볼륨에 저장됩니다. 다음 실행부터는 `docker start foodsafety-postgres`만 실행하면 됩니다.

이미 설치된 PostgreSQL을 사용한다면 해당 데이터베이스에서 `vector` 확장을 활성화하고 `backend/core/config.py`의 `CONNECTION_STRING`을 로컬 환경에 맞게 변경합니다. 자세한 DB 설정은 [백엔드 README](../backend/README.md#로컬-데이터베이스-구성)를 참고하세요.

### 5. 식품공전 데이터 전처리 및 적재

가상환경이 활성화된 `backend` 디렉터리에서 먼저 Markdown 문서를 전처리합니다.

```powershell
python -m rag.preprocessor
```

새 로컬 DB에서는 `foodsafety_fd_cd` 벡터 테이블을 한 번만 초기화합니다.

```powershell
python -c "from langchain_postgres import PGEngine; from core.config import CONNECTION_STRING; engine = PGEngine.from_connection_string(url=CONNECTION_STRING); engine.init_vectorstore_table(table_name='foodsafety_fd_cd', vector_size=1024)"
```

이어서 전처리된 데이터를 임베딩하고 로컬 DB에 적재합니다.

```powershell
python -m rag.load
```

처리 과정은 다음과 같습니다.

```text
data/md/*.md
    → rag.preprocessor
data/doc.jsonl
    → foodsafety_fd_cd 테이블 초기화 (최초 1회)
    → rag.load + Voyage AI 임베딩
로컬 PostgreSQL의 foodsafety_fd_cd 테이블
```

`rag.load`를 실행하려면 `VOYAGE_API_KEY`와 실행 중인 PostgreSQL이 필요합니다. Docker 환경에서는 다음 명령으로 적재 결과를 확인합니다.

```powershell
docker exec foodsafety-postgres psql -U langchain -d langchain -c "SELECT COUNT(*) FROM foodsafety_fd_cd;"
```

> 전처리는 다시 실행할 수 있지만 같은 DB에 `rag.load`를 반복 실행하면 동일한 문서가 중복 저장될 수 있습니다.

상세한 전처리 과정과 검증 방법은 [백엔드 README](../backend/README.md#데이터-전처리-및-적재)를 참고하세요.

### 6. 백엔드 실행

`backend` 디렉터리에서 다음 명령을 실행합니다.

```powershell
uvicorn main:app --reload
```

정상적으로 실행되면 다음 주소를 확인할 수 있습니다.

- 백엔드 API: <http://127.0.0.1:8000>
- Swagger UI: <http://127.0.0.1:8000/docs>

### 7. 프런트엔드 설치 및 실행

백엔드는 그대로 실행해 두고 **새 터미널**을 엽니다. 프로젝트 루트의 `frontend` 디렉터리로 이동합니다.

```powershell
cd foodsafety-ai-chatbot\frontend
npm install
npm run dev
```

이미 프로젝트 루트에 있다면 `cd frontend`만 실행하면 됩니다.

정상적으로 실행되면 브라우저에서 <http://localhost:5173>에 접속합니다.

### 8. 프런트엔드 환경 변수 설정 (선택)

백엔드가 기본 주소가 아닌 곳에서 실행된다면 `frontend/.env` 파일을 생성합니다.

```dotenv
VITE_API_URL=http://127.0.0.1:8000
```

환경 변수가 없으면 `http://127.0.0.1:8000`을 사용합니다. `.env`를 변경한 뒤에는 Vite 개발 서버를 다시 실행해야 합니다.

### 9. 실행 확인

두 터미널에 다음 프로세스가 함께 실행 중이어야 합니다.

| 구분 | 실행 명령 | 접속 주소 |
| --- | --- | --- |
| Backend | `uvicorn main:app --reload` | <http://127.0.0.1:8000/docs> |
| Frontend | `npm run dev` | <http://localhost:5173> |

Vite가 `5173`이 아닌 다른 포트에서 실행되면 백엔드의 `CORS_ORIGINS`에도 해당 주소를 추가해야 합니다.

## API 연동

위젯은 다음 형식으로 백엔드에 요청합니다.

```http
POST {VITE_API_URL}/chat
Content-Type: application/json
```

```json
{
  "message": "사용자 질문",
  "thread_id": "default"
}
```

```json
{
  "answer": "챗봇 답변"
}
```

백엔드의 CORS 설정에는 프런트엔드 주소가 허용되어 있어야 합니다.

## 명령어

| 명령어 | 설명 |
| --- | --- |
| `npm run dev` | 개발 서버 실행 |
| `npm run build` | 배포용 빌드 생성 |
| `npm run preview` | 배포용 빌드 미리보기 |
| `npm run lint` | ESLint 검사 |

## 프로젝트 구조

```text
frontend/
├── public/                  # 정적 이미지와 아이콘
├── src/
│   ├── component/
│   │   └── ChatWidget.jsx   # 채팅 UI와 API 통신
│   ├── App.jsx
│   ├── App.css
│   ├── index.css
│   └── main.jsx
├── .env                     # 로컬 API 주소
├── package.json
└── vite.config.js
```

## 프로덕션 빌드

```powershell
npm run build
npm run preview
```

빌드 결과는 `dist/` 디렉터리에 생성되며 Git에서 제외됩니다.
