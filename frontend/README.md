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
- Neon 프로젝트 또는 공유받은 Neon DB 접근 권한
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

`backend/.env.example`을 복사해 `.env` 파일을 만들고 다음 값을 입력합니다.

```powershell
Copy-Item .env.example .env
```

```dotenv
DATABASE_URL=postgresql://[user]:[password]@[neon-hostname]/[database]?sslmode=require&channel_binding=require
ANTHROPIC_API_KEY=your_anthropic_api_key
VOYAGE_API_KEY=your_voyage_api_key
```

Neon 콘솔에서 **Connect**를 눌러 연결 문자열을 복사할 수 있습니다. `.env`는 DB 비밀번호를 포함하므로 Git에 커밋하거나 공개하지 않습니다.

### 4. Neon PostgreSQL 및 pgvector 준비

Neon 콘솔의 **SQL Editor**에서 대상 데이터베이스를 선택하고 pgvector 확장을 한 번 활성화합니다.

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

팀의 Neon DB에 이미 `foodsafety_fd_cd` 테이블과 데이터가 있다면 연결 문자열만 설정하고 다음 전처리·적재 단계는 건너뜁니다.

자세한 DB 설정은 [백엔드 README](../backend/README.md#neon-데이터베이스-구성)를 참고하세요.

### 5. 식품공전 데이터 전처리 및 적재

가상환경이 활성화된 `backend` 디렉터리에서 먼저 Markdown 문서를 전처리합니다.

```powershell
python -m rag.preprocessor
```

비어 있는 새 Neon DB에서는 `foodsafety_fd_cd` 벡터 테이블을 한 번만 초기화합니다.

```powershell
python -c "from langchain_postgres import PGEngine; from core.config import CONNECTION_STRING; engine = PGEngine.from_connection_string(url=CONNECTION_STRING); engine.init_vectorstore_table(table_name='foodsafety_fd_cd', vector_size=1024)"
```

이어서 전처리된 데이터를 임베딩하고 Neon DB에 적재합니다.

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
Neon PostgreSQL의 foodsafety_fd_cd 테이블
```

`rag.load`를 실행하려면 `DATABASE_URL`과 `VOYAGE_API_KEY`가 필요합니다. Neon SQL Editor에서 다음 쿼리로 적재 결과를 확인합니다.

```sql
SELECT COUNT(*) AS document_count FROM foodsafety_fd_cd;
```

> 전처리는 다시 실행할 수 있지만 공유 Neon DB에 `rag.load`를 반복 실행하면 동일한 문서가 중복 저장될 수 있습니다. 팀의 DB 담당자만 적재를 수행하세요.

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
