#!/usr/bin/env python3
"""
④ 디자인 에이전트 (Gemini 2.5 Flash)
page_copy.json + research_report.json → design_spec.json
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gemini_client import generate_json

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"

SYSTEM_INSTRUCTION = """당신은 이커머스 상세페이지 디자인 디렉터입니다.
한국 이커머스 트렌드(쿠팡, 네이버 스마트스토어)에 맞는 모던하고 깔끔한 디자인을 설계합니다.
모든 색상은 hex 코드로, 폰트 사이즈는 px 단위로 지정하세요.
반드시 한국어로 작성하세요."""


def main():
    # 입력 파일 읽기
    copy_path = OUTPUT_DIR / "page_copy.json"
    research_path = OUTPUT_DIR / "research_report.json"

    if not copy_path.exists():
        print(f"ERROR: {copy_path} 파일이 없습니다.")
        sys.exit(1)
    if not research_path.exists():
        print(f"ERROR: {research_path} 파일이 없습니다.")
        sys.exit(1)

    with open(copy_path, "r", encoding="utf-8") as f:
        copy_data = json.load(f)
    with open(research_path, "r", encoding="utf-8") as f:
        research = json.load(f)

    print("디자인 설계 시작...")
    print("Gemini 2.5 Flash 호출 중...")

    prompt = f"""아래 카피와 리서치 결과를 기반으로 상세페이지 10개 섹션의 디자인 스펙을 설계하세요.

## 카피 데이터
{json.dumps(copy_data, ensure_ascii=False, indent=2)}

## 리서치 결과
추천 톤앤매너: {research.get('recommended_tone', '')}

## 설계할 10개 섹션

| 섹션 | 권장 사이즈 | 레이아웃 |
|------|-----------|---------|
| 01_hero | 1080×1080 | 중앙 대형 텍스트, 배지 |
| 02_pain_point | 1080×800 | 아이콘+텍스트 리스트 |
| 03_solution | 1080×700 | 중앙 강조 |
| 04_features | 1080×1000 | 2×2 카드 그리드 |
| 05_specs | 1080×800 | 테이블 레이아웃 |
| 06_how_to_use | 1080×800 | 번호 스텝 리스트 |
| 07_difference | 1080×800 | 좌우 비교 테이블 |
| 08_reviews | 1080×900 | 카드 리스트 |
| 09_faq | 1080×800 | Q&A 리스트 |
| 10_cta | 1080×600 | 중앙 집중, 강조 배경 |

## 디자인 원칙
- 섹션 간 배경색 교차 (시각적 리듬감)
- 충분한 여백 (최소 60px 마진)
- 가독성 최우선 (텍스트-배경 대비)
- 모던하고 깔끔한 한국 이커머스 스타일

## 출력 JSON 스키마
{{
  "global_style": {{
    "primary_color": "#hex",
    "secondary_color": "#hex",
    "accent_color": "#hex",
    "bg_color": "#hex",
    "text_color": "#hex",
    "mood": "분위기 설명"
  }},
  "sections": [
    {{
      "id": "01_hero",
      "width": 1080,
      "height": 1080,
      "bg_color": "#hex",
      "text_color": "#hex",
      "accent_color": "#hex",
      "layout": "centered",
      "elements": [
        {{
          "type": "text 또는 rectangle 또는 badge 또는 line 또는 icon_text",
          "설명": "각 요소의 속성"
        }}
      ]
    }}
  ]
}}

각 섹션의 elements에는 실제 Pillow로 렌더링할 수 있는 구체적 요소를 포함하세요:
- text: content, x, y, font_size, font_weight(bold/normal), color, align(left/center/right), max_width
- rectangle: x, y, width, height, fill, radius, outline, outline_width
- line: x1, y1, x2, y2, color, width
- badge: content, x, y, bg_color, text_color, font_size, padding
- icon_text: icon(이모지), label, x, y, font_size, color

카피 데이터의 실제 텍스트를 text 요소의 content에 그대로 넣으세요."""

    result = generate_json(prompt, SYSTEM_INSTRUCTION)

    # 저장
    output_path = OUTPUT_DIR / "design_spec.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, ensure_ascii=False, indent=2, fp=f)

    print(f"완료: {output_path}")
    print(f"글로벌 스타일: {result.get('global_style', {}).get('mood', '')}")
    print(f"섹션 {len(result.get('sections', []))}개 설계")


if __name__ == "__main__":
    main()
