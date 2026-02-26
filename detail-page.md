이커머스 상세페이지를 자동 생성합니다. Claude + Gemini 하이브리드 구조로 5단계 에이전트가 순차 협업하여 최종 10개 PNG 파일을 산출합니다.

## 입력
상품 정보: $ARGUMENTS

## 아키텍처 (하이브리드)
- Step 1 정보수집: **Claude** Task (WebSearch 활용)
- Step 2 리서치: **Gemini 2.5 Flash** (시장 분석 강점)
- Step 3 카피라이팅: **Claude** Task (한국어 카피 강점)
- Step 4 디자인: **Gemini 2.5 Flash** (비주얼 디렉션 강점)
- Step 5 프롬프트: **Claude** Task (JSON 구조화 강점)
- Step 6 렌더링: **Pillow** Python (비용 0원)

## 워크플로우

아래 6단계를 **반드시 순서대로** 실행합니다.
각 에이전트는 `output/` 폴더에 결과 JSON을 저장하며, 다음 에이전트가 이를 읽어서 작업합니다.

output 폴더 경로: 현재 프로젝트의 `output/` 디렉터리
스크립트 경로: 현재 프로젝트의 `detail-page-agents/` 디렉터리

---

### Step 1: 정보수집 에이전트 (Claude)
Task(general-purpose)로 실행합니다.

프롬프트:
```
당신은 이커머스 상세페이지 제작을 위한 정보수집 전문가입니다.

[상품 정보]
{사용자가 입력한 $ARGUMENTS 전체를 여기에 포함}

아래 작업을 수행하세요:
1. 상품명, 브랜드, 카테고리, 가격, 옵션, 스펙을 정리
2. 이 상품의 USP(차별점) 3~5개 도출
3. 타겟 고객층 정의
4. 부족한 정보는 WebSearch로 보완
5. 결과를 output/product_brief.json으로 저장

JSON 스키마: {"product_name","brand","category","price":{"regular","sale","currency"},"options":[],"specs":{},"usp":[],"target_audience":{"age","gender","lifestyle"},"use_cases":[],"keywords":[]}
```

---

### Step 2: 리서치 에이전트 (Gemini)
Step 1 완료 후 **Bash**로 실행합니다:

```bash
python3 detail-page-agents/agent_researcher.py
```

이 스크립트가 Gemini 2.5 Flash API를 호출하여 경쟁사 분석, 소비자 인사이트, 셀링포인트를 도출하고 output/research_report.json에 저장합니다.

---

### Step 3: 카피라이팅 에이전트 (Claude)
Step 2 완료 후 Task(general-purpose)로 실행합니다.

프롬프트:
```
당신은 이커머스 상세페이지 카피라이터입니다.

output/product_brief.json과 output/research_report.json을 먼저 Read로 읽으세요.

아래 10개 섹션의 카피를 작성하세요:
01_hero: 헤드라인(15자이내) + 서브카피 + 배지
02_pain_point: 공감 타이틀 + 고민 리스트 3~4개
03_solution: 선언 타이틀 + 해결 설명 + 키메시지
04_features: 기능 카드 3~4개 (아이콘키워드 + 기능명 + 혜택 설명)
05_specs: 스펙 테이블 5~8항목
06_how_to_use: 3~4 스텝 (번호 + 제목 + 설명)
07_difference: "일반 vs 우리" 비교 3~4항목
08_reviews: 후기 3~4개 (별점 + 한줄평 + 상세)
09_faq: Q&A 4~5개
10_cta: 행동유도 헤드라인 + 서브카피 + 버튼텍스트

기능이 아닌 혜택(benefit) 관점으로 작성하세요.
결과를 output/page_copy.json으로 저장하세요.
```

---

### Step 4: 디자인 에이전트 (Gemini)
Step 3 완료 후 **Bash**로 실행합니다:

```bash
python3 detail-page-agents/agent_designer.py
```

이 스크립트가 Gemini 2.5 Flash API를 호출하여 컬러 팔레트, 10개 섹션 레이아웃, 요소별 디자인 스펙을 설계하고 output/design_spec.json에 저장합니다.

---

### Step 5: 프롬프트 에이전트 (Claude)
Step 4 완료 후 Task(general-purpose)로 실행합니다.

프롬프트:
```
당신은 상세페이지 최종 프로덕션 엔지니어입니다.

output/page_copy.json과 output/design_spec.json을 Read로 읽으세요.

두 JSON을 합쳐서 Pillow(Python) 렌더링 스크립트가 바로 사용할 수 있는 render_data.json을 만드세요.

각 섹션(10개)에 대해:
- id: "01_hero" 형식
- filename: "01_hero.png" 형식
- canvas: {width, height}
- background: hex 색상
- elements: 배열 — 아래 타입 사용:
  - text: {type:"text", content, x, y, font_size, font_weight, color, align, max_width}
  - rectangle: {type:"rectangle", x, y, width, height, fill, radius}
  - line: {type:"line", x1, y1, x2, y2, color, width}
  - badge: {type:"badge", content, x, y, bg_color, text_color, font_size, padding}
  - icon_text: {type:"icon_text", icon(이모지), label, x, y, font_size, color}

중요 규칙:
- 텍스트 위치는 캔버스 내 최소 60px 마진
- 긴 텍스트는 max_width 설정 (자동 줄바꿈용)
- 한국어 카피 원본 그대로 유지
- 시각적 계층: 헤드라인(큰) > 서브카피(중) > 본문(작)
- 각 섹션의 image_prompt도 포함 (이미지 AI용 영문 프롬프트)

결과를 output/render_data.json으로 저장하세요.
```

---

### Step 6: PNG 렌더링
모든 에이전트 완료 후 **Bash**로 실행합니다:

```bash
python3 detail-page-agents/render.py
```

이 스크립트는 output/render_data.json을 읽어서 10개 PNG 파일을 output/ 폴더에 생성합니다.

---

## 완료 후 출력

최종 산출물을 사용자에게 보고합니다:
- 생성된 10개 PNG 파일 경로 목록
- 각 섹션별 핵심 카피 요약
- 이미지 AI 프롬프트 (별도 활용 가능)
- 개선/수정이 필요한 부분 안내
