# 디자인 자동 생성기

> Claude Code + Gemini 하이브리드 AI 에이전트가 협업하여 이커머스 상세페이지 10개 섹션을 PNG로 자동 생성합니다.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Claude Code](https://img.shields.io/badge/Claude_Code-CLI-orange)
![Gemini](https://img.shields.io/badge/Gemini_2.5-Flash-green)
![Pillow](https://img.shields.io/badge/Pillow-Rendering-yellow)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 결과물 예시

상품 정보만 입력하면 아래와 같은 10개 섹션 상세페이지가 자동 생성됩니다.

| 섹션 | 설명 |
|------|------|
| 01. Hero | 메인 비주얼 + 가격 + 할인 배지 |
| 02. Photo Banner | 풀폭 라이프스타일 포토 |
| 03. Key Numbers | 핵심 스펙 숫자 강조 (대형 타이포) |
| 04. Pain & Solution | 고민 공감 → 해결책 제시 |
| 05. Features | 기능 카드 그리드 |
| 06. Spec Table | 상세 스펙 테이블 |
| 07. Lifestyle Photo | 사용 장면 포토 배너 |
| 08. Comparison | 일반 제품 vs 우리 제품 비교 |
| 09. Reviews | 고객 후기 카드 |
| 10. CTA | 구매 유도 (가격 + 버튼) |

최종 출력: **1080px 폭 10개 PNG** + **1개 통합 이미지**

---

## 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code CLI                       │
│                  /detail-page 스킬 실행                   │
└──────────────────────┬──────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
  ┌─────────┐   ┌───────────┐   ┌───────────┐
  │ Claude  │   │  Gemini   │   │  Pillow   │
  │ (Text)  │   │ (Vision)  │   │ (Render)  │
  └─────────┘   └───────────┘   └───────────┘

Step 1  정보수집 ──── Claude ────→ product_brief.json
Step 2  리서치 ────── Gemini ────→ research_report.json
Step 3  카피라이팅 ── Claude ────→ page_copy.json
Step 4  디자인 ────── Gemini ────→ design_spec.json
Step 5  프롬프트 ──── Claude ────→ render_data.json
Step 6  렌더링 ────── Pillow ────→ 10개 PNG + 통합 이미지
```

### 왜 하이브리드?

| 역할 | AI | 이유 |
|------|-----|------|
| 정보수집 | Claude | WebSearch 기반 상품 조사 |
| 리서치 | Gemini 2.5 Flash | 시장 분석, 경쟁사 비교에 강점 |
| 카피라이팅 | Claude | 한국어 카피 품질 우수 |
| 디자인 | Gemini 2.5 Flash | 비주얼 디렉션, 레이아웃 설계 |
| 프롬프트 | Claude | JSON 구조화, 데이터 병합 |
| 렌더링 | Pillow | 비용 0원, 로컬 실행 |

---

## 설치

### 1. 사전 요구사항

- **Python 3.10+**
- **Claude Code CLI** ([설치 가이드](https://docs.anthropic.com/en/docs/claude-code))
- **Gemini API Key** (무료) — [Google AI Studio](https://aistudio.google.com/)

### 2. 프로젝트 클론

```bash
git clone https://github.com/alskdjf212/detail-page-generator.git
cd detail-page-generator
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. API 키 설정

프로젝트 루트에 `.env` 파일 생성:

```bash
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### 5. Claude Code 스킬 등록

`detail-page.md` 파일을 Claude Code 프로젝트의 스킬 폴더에 복사:

```bash
# 프로젝트 레벨 스킬로 등록
mkdir -p .claude/commands
cp detail-page.md .claude/commands/
```

### 6. 출력 폴더 생성

```bash
mkdir -p output
```

---

## 사용법

### Claude Code CLI에서 실행

```bash
claude

# Claude Code 안에서:
/detail-page 캠핑 의자, 브랜드: 캠핏, 가격: 59000원, 내하중 150kg, 무게 2.5kg, 600D 옥스포드 원단
```

상품 정보를 자연어로 입력하면 6단계 에이전트가 순차 실행됩니다.

### 개별 단계 수동 실행

각 에이전트를 개별적으로 실행할 수도 있습니다:

```bash
# Step 2: 리서치 (Gemini)
python3 agent_researcher.py

# Step 4: 디자인 (Gemini)
python3 agent_designer.py

# Step 6: 렌더링 (Pillow)
python3 render.py
```

### 사진 추가 (선택)

`output/` 폴더에 사진을 넣으면 자동으로 섹션에 배치됩니다:

| 파일명 | 용도 | 권장 사이즈 |
|--------|------|------------|
| `product_photo.png` | 제품 사진 (히어로, CTA) | 1000×1000px+ |
| `photo_person_chair.jpg` | 인물 + 제품 (포토배너) | 1080×1620px |
| `photo_scene.jpg` | 사용 장면 (핵심숫자 배경) | 1080×720px |
| `photo_family.jpg` | 라이프스타일 (풀폭 배너) | 1080×720px |
| `photo_nature.jpg` | 자연 배경 (후기 배경) | 1080×720px |
| `photo_lifestyle.jpg` | 라이프스타일 참고 | 1080×720px |

---

## 파일 구조

```
detail-page-generator/
├── README.md                  # 이 문서
├── requirements.txt           # Python 패키지
├── .env                       # Gemini API Key (직접 생성)
│
├── detail-page.md             # Claude Code 스킬 정의
├── gemini_client.py           # Gemini API 클라이언트
├── agent_researcher.py        # Step 2: 리서치 에이전트
├── agent_designer.py          # Step 4: 디자인 에이전트
├── render.py                  # Step 6: PNG 렌더러
│
└── output/                    # 생성된 파일들
    ├── product_brief.json     # Step 1 결과
    ├── research_report.json   # Step 2 결과
    ├── page_copy.json         # Step 3 결과
    ├── design_spec.json       # Step 4 결과
    ├── render_data.json       # Step 5 결과
    ├── 01_hero.png            # 섹션 이미지들
    ├── ...
    ├── 10_cta.png
    └── detail_page_full.png   # 통합 이미지
```

---

## 커스터마이징

### 섹션 구성 변경

`detail-page.md`의 Step 3 카피라이팅 프롬프트에서 10개 섹션을 수정:

```
01_hero: 헤드라인(15자이내) + 서브카피 + 배지
02_pain_point: 공감 타이틀 + 고민 리스트 3~4개
...
```

### 디자인 스타일 변경

`agent_designer.py`의 `SYSTEM_INSTRUCTION`을 수정:

```python
SYSTEM_INSTRUCTION = """당신은 이커머스 상세페이지 디자인 디렉터입니다.
한국 이커머스 트렌드(쿠팡, 네이버 스마트스토어)에 맞는 모던하고 깔끔한 디자인을 설계합니다.
..."""
```

### 캔버스 크기 변경

`render.py`의 기본값은 `1080px` 폭이며, 각 섹션 높이는 `render_data.json`에서 조절됩니다.

### 폰트 변경

`render.py`의 `FONT_PATHS` 배열에 원하는 폰트 경로 추가:

```python
FONT_PATHS = [
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",  # macOS
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",  # Linux (나눔고딕)
]
```

---

## 기술 스택

| 구성요소 | 기술 | 비용 |
|---------|------|------|
| 오케스트레이터 | Claude Code CLI | Claude 구독 |
| 카피/구조화 | Claude (Task agent) | Claude 구독 포함 |
| 리서치/디자인 | Gemini 2.5 Flash API | **무료** (Free tier) |
| 렌더링 | Pillow (Python) | **무료** (로컬) |
| 폰트 | Apple SD Gothic Neo | macOS 기본 |

---

## 워크플로우 상세

### Step 1: 정보수집 (Claude)
- 사용자 입력에서 상품명, 브랜드, 가격, 스펙 추출
- WebSearch로 부족한 정보 보완
- USP(차별점) 3~5개 도출

### Step 2: 리서치 (Gemini)
- 경쟁사 3~5개 분석 (가격, 강점, 약점)
- 소비자 구매 결정 요인 분석
- 셀링포인트 우선순위 도출

### Step 3: 카피라이팅 (Claude)
- 10개 섹션별 카피 작성
- 기능(feature)이 아닌 혜택(benefit) 관점
- 한국어 자연스러운 톤

### Step 4: 디자인 (Gemini)
- 컬러 팔레트 설계
- 섹션별 레이아웃, 요소 배치
- 타이포그래피 계층 설정

### Step 5: 프롬프트 (Claude)
- 카피 + 디자인 JSON 병합
- Pillow 렌더링용 좌표/크기 지정
- 최종 render_data.json 생성

### Step 6: 렌더링 (Pillow)
- JSON → PNG 변환
- 사진 합성 (crop, resize, overlay)
- 10개 섹션 + 1개 통합 이미지 출력

---

## 제한사항

- macOS 환경에 최적화 (AppleSDGothicNeo 폰트)
- Linux/Windows에서는 한국어 폰트 별도 설치 필요
- Gemini Free tier 일일 호출 한도 존재
- 이미지 AI 생성이 아닌 **Pillow 기반 그래픽 렌더링** (일러스트/실사 이미지 X)

---

## 라이선스

MIT License

---

## 만든 사람

Claude Code + Gemini 하이브리드 AI 에이전트 시스템으로 제작되었습니다.
