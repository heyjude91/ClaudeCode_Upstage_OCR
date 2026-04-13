# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 프로젝트 개요

**AI 영수증 지출 관리 시스템** — 영수증 이미지(JPG/PNG/PDF)를 업로드하면 Upstage Vision LLM이 OCR로 항목을 추출하고, SQLite에 저장해 통계·차트로 시각화하는 웹 앱.

- 기획 문서: `개요서_AI_영수증_지출관리.md`, `PRD_AI_영수증_지출관리.md`
- 테스트용 영수증 샘플: `images/` (이마트·스타벅스·CU·롯데마트·이케아·유니클로·CGV·메가박스·의료·택시 등 11종)

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| 백엔드 | Python 3.11+, FastAPI 0.110+, LangChain 1.2+, langchain-upstage 0.7+, SQLAlchemy, SQLite |
| 프론트엔드 | React 18+, Vite 5+, TailwindCSS 3+, Recharts 2+, Axios 1.6+, React Router, Heroicons |
| AI | Upstage Document AI (Vision LLM) — `UPSTAGE_API_KEY` 필요 |

---

## 환경 설정

### 필수 환경변수 (`.env`)

```
UPSTAGE_API_KEY=up-xxxxxxxxxxxxxxxx
UPLOAD_DIR=./uploads
DATABASE_URL=./data/receipts.db
MAX_FILE_SIZE_MB=10
```

> `.env`는 반드시 `.gitignore`에 포함. `uploads/`, `data/`도 제외.

---

## 개발 명령어

### 백엔드 (FastAPI)

```bash
# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/Scripts/activate   # Windows
source .venv/bin/activate        # macOS/Linux

# 패키지 설치
pip install -r backend/requirements.txt

# 개발 서버 실행 (핫리로드)
uvicorn backend.main:app --reload --port 8000

# API 문서 확인
open http://localhost:8000/docs
```

### 프론트엔드 (React + Vite)

```bash
cd frontend
npm install
npm run dev        # 개발 서버 (http://localhost:5173)
npm run build      # 프로덕션 빌드
npm run preview    # 빌드 결과 로컬 미리보기
```

---

## 아키텍처

### 데이터 흐름

```
Browser → POST /api/receipts/upload (multipart)
        → ocr_service.py : ChatUpstage Vision LLM → JSON
        → receipt_service.py : SQLite 저장
        → 응답: receipt + items JSON

Browser → GET /api/receipts?page=1&category=식료품
        → receipt_service.py : 동적 필터 쿼리
        → 응답: 목록 + 페이지 메타

Browser → GET /api/stats/summary?date_from=&date_to=
        → stats_service.py : 월별·카테고리별 집계
        → Recharts 차트 렌더링
```

### 백엔드 레이어 구조

```
routers/      # HTTP 진입점 — 경로 파라미터 파싱, 응답 직렬화
services/     # 비즈니스 로직 — OCR 파이프라인, CRUD, 통계 집계
models/       # SQLAlchemy ORM — receipts, receipt_items 테이블
schemas/      # Pydantic — ReceiptCreate / ReceiptRead / ReceiptUpdate
```

- `receipts.id` ↔ `receipt_items.receipt_id` (FK, ON DELETE CASCADE)
- 업로드 파일은 `uploads/` 에 저장, `StaticFiles`로 서빙
- OCR 실패 시 1회 재시도, 30초 타임아웃

### 프론트엔드 구조

```
pages/        # 화면 단위 (Dashboard, Upload, ExpenseList, ExpenseDetail, Stats)
components/   # layout/, receipt/, charts/, common/ 로 역할 분리
api/          # Axios 인스턴스 + 엔드포인트별 함수 (receipts.js, stats.js, categories.js)
hooks/        # useReceipts, useStats — 서버 상태 관리
utils/        # formatters.js (₩ 포맷, 날짜), constants.js (카테고리 컬러 매핑)
```

- Vite 개발 서버에서 `/api` → `http://localhost:8000` 프록시 (`vite.config.js`)
- 카테고리 컬러: 식료품 `#6366F1`, 외식 `#F97316`, 쇼핑 `#EC4899`, 교통 `#14B8A6`, 의료 `#EF4444`, 문화 `#A855F7`, 기타 `#9CA3AF`

---

## API 엔드포인트

| Method | URL | 설명 |
|--------|-----|------|
| POST | `/api/receipts/upload` | 파일 업로드 + OCR 분석 + DB 저장 |
| GET | `/api/receipts` | 목록 조회 (`date_from`, `date_to`, `category`, `store_name`, `page`, `limit`) |
| GET | `/api/receipts/{id}` | 상세 조회 (items 포함) |
| PUT | `/api/receipts/{id}` | 수정 |
| DELETE | `/api/receipts/{id}` | 삭제 (CASCADE) |
| GET | `/api/stats/summary` | 월별·카테고리별 통계 |
| GET | `/api/categories` | 카테고리 목록 |

오류 응답 형식: `{ "error": { "code": "INVALID_FILE_TYPE", "message": "..." } }`

---

## 개발 우선순위 (MoSCoW)

- **P0 (Must)**: 업로드 → OCR → 저장 → 목록/상세 CRUD → 수정/삭제 → 오류 처리
- **P1 (Should)**: 필터 조회, 3종 차트, 썸네일·이미지 뷰어, 대시보드, 페이지네이션
- **P2 (Could)**: 반응형 모바일, 중복 업로드 경고, 스켈레톤 UI
- **Out (v2+)**: 회원가입/로그인, 내보내기, 예산 알림

전체 기능-우선순위 매트릭스: `PRD_AI_영수증_지출관리.md` § 12.2 참조.

---

## PRD 동기화 규칙

코드 작업 후 아래 조건에 해당하면 `PRD_AI_영수증_지출관리.md`의 관련 섹션을 반드시 업데이트한다.

### 업데이트 트리거 조건

| 변경 유형 | 업데이트할 PRD 섹션 |
|-----------|-------------------|
| API 엔드포인트 추가·수정·삭제 | API 명세 섹션 |
| DB 스키마 변경 (컬럼·테이블·관계) | 데이터 모델 섹션 |
| 새 기능 구현 또는 기존 기능 제거 | 기능 목록 / MoSCoW 우선순위 섹션 |
| 기술 스택 변경 (패키지 추가·제거) | 기술 스택 섹션 |
| 아키텍처 구조 변경 (레이어·파일 구조) | 시스템 아키텍처 섹션 |
| 오류 처리 방식 변경 | 오류 처리 섹션 |
| 환경변수·설정 변경 | 환경 설정 섹션 |

### 업데이트 제외 조건

아래 변경은 PRD를 건드리지 않는다.

- 리팩토링 (동작 변경 없이 코드 정리)
- 버그 수정 (기존 스펙 범위 내)
- 스타일·CSS·이미지 등 UI 비기능 변경
- 테스트 코드 추가·수정
- 주석·문서 주석(docstring) 수정

### 업데이트 방식

1. 변경된 파일과 diff를 먼저 확인한다.
2. 위 트리거 조건 중 해당 항목을 식별한다.
3. PRD의 **해당 섹션만** 수정한다 — 무관한 섹션은 건드리지 않는다.
4. 날짜·버전 표기가 있는 섹션이면 수정일을 함께 갱신한다.
5. 코드 작업 완료 응답 말미에 "PRD § <섹션명> 업데이트됨" 한 줄로 알린다.

---

## 테스트용 샘플 이미지

`images/` 디렉토리의 영수증을 OCR 정확도 검증에 활용:

| 파일 | 업종 |
|------|------|
| `01_emart.png` | 대형마트 (식료품) |
| `02_starbucks.png` | 카페 (외식) |
| `03_cu.jpg` | 편의점 (식료품) |
| `03_lotte_depart.png` | 백화점 (쇼핑) |
| `04_lotteria.png` | 패스트푸드 (외식) |
| `05_ikea.png` | 가구 (쇼핑) |
| `06_uniqlo.png` | 의류 (쇼핑) |
| `07_cgv.png` | 영화관 (문화) |
| `08_megabox.png` | 영화관 (문화) |
| `09_medical.png`, `10_medical.png` | 의료 |
| `11_taxi.png` | 교통 |
| `GS25편의점_영수증.pdf` | PDF 형식 영수증 |
