# 상품공전 안내 챗봇

React와 Vite로 만든 상품공전 안내용 채팅 위젯입니다. 사용자의 질문을 백엔드 채팅 API로 전송하고 응답을 대화형 UI로 보여줍니다.

## 주요 기능

- 플로팅 버튼으로 채팅창 열기 및 닫기
- 사용자 질문과 챗봇 답변을 말풍선 형태로 표시
- Enter 키 또는 전송 버튼으로 메시지 전송
- 답변 대기 중 로딩 애니메이션 표시
- API 요청 실패 시 오류 메시지 표시
- 홈, 대화, 설정 탭 UI 제공
- 채팅 패널 크기 조절 지원

## 기술 스택

- React 19
- Vite 8
- JavaScript (ES Modules)
- Lucide React
- ESLint / Prettier

## 시작하기

### 1. 의존성 설치

```bash
npm install
```

### 2. 환경 변수 설정

프로젝트 루트의 `.env` 파일에 백엔드 API 주소를 지정합니다.

```env
VITE_API_URL=http://127.0.0.1:8000
```

설정하지 않으면 `http://127.0.0.1:8000`을 기본값으로 사용합니다.

### 3. 개발 서버 실행

```bash
npm run dev
```

터미널에 표시된 로컬 주소로 접속하면 채팅 위젯을 확인할 수 있습니다.

## API 연동 규격

```http
POST {VITE_API_URL}/chat
Content-Type: application/json
```

요청 본문:

```json
{
  "message": "사용자 질문",
  "thread_id": "default"
}
```

응답 본문:

```json
{
  "answer": "챗봇 답변"
}
```

백엔드는 프론트엔드 출처(origin)를 허용하도록 CORS를 설정해야 합니다.

## 명령어

| 명령어 | 설명 |
| --- | --- |
| `npm run dev` | 개발 서버 실행 |
| `npm run build` | 프로덕션 빌드 생성 |
| `npm run preview` | 프로덕션 빌드 미리보기 |
| `npm run lint` | ESLint 검사 실행 |

## 프로젝트 구조

```text
ReactProject/
├─ public/
│  └─ cha_user-serv01.png
├─ src/
│  ├─ component/
│  │  └─ ChatWidget.jsx
│  ├─ App.jsx
│  ├─ App.css
│  ├─ index.css
│  └─ main.jsx
├─ .env
├─ package.json
└─ vite.config.js
```

`App.jsx`가 `ChatWidget`을 렌더링하며, 채팅 상태 관리와 API 통신 로직은 `src/component/ChatWidget.jsx`에 있습니다.

## 프로덕션 빌드

```bash
npm run build
npm run preview
```

빌드 결과물은 `dist/` 디렉터리에 생성됩니다.
