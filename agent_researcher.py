#!/usr/bin/env python3
"""
② 리서치 에이전트 (Gemini 2.5 Flash)
product_brief.json → research_report.json
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gemini_client import generate_json

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"

SYSTEM_INSTRUCTION = """당신은 이커머스 시장 리서치 전문가입니다.
상품 정보를 분석하여 경쟁사 비교, 소비자 인사이트, 셀링포인트를 도출합니다.
반드시 한국어로 작성하세요."""


def main():
    # product_brief.json 읽기
    brief_path = OUTPUT_DIR / "product_brief.json"
    if not brief_path.exists():
        print(f"ERROR: {brief_path} 파일이 없습니다.")
        print("먼저 Step 1 (정보수집 에이전트)을 실행하세요.")
        sys.exit(1)

    with open(brief_path, "r", encoding="utf-8") as f:
        brief = json.load(f)

    print(f"리서치 시작: {brief.get('product_name', '상품')}")
    print("Gemini 2.5 Flash 호출 중...")

    prompt = f"""아래 상품 정보를 기반으로 시장 리서치를 수행하세요.

## 상품 정보
{json.dumps(brief, ensure_ascii=False, indent=2)}

## 수행할 작업

### 1. 경쟁사 분석
- 동일 카테고리 경쟁 상품 3~5개 조사
- 각 경쟁 상품의 가격대, 강점, 약점 분석

### 2. 소비자 인사이트
- 이 카테고리에서 소비자가 가장 중시하는 구매 결정 요인
- 자주 언급되는 칭찬/불만 포인트
- 구매 전 망설이는 이유 (hesitation reasons)

### 3. 셀링포인트 전략
- 우선순위 정렬된 셀링포인트 (1위가 가장 강력)
- 각 포인트에 대한 근거
- 추천 톤앤매너 (신뢰감/감성적/전문적/위트 등)

## 출력 JSON 스키마
{{
  "competitors": [
    {{"name": "경쟁상품명", "price": "가격", "strengths": ["강점1"], "weaknesses": ["약점1"]}}
  ],
  "buyer_insights": {{
    "purchase_factors": ["구매결정요인1", "구매결정요인2"],
    "common_praise": ["칭찬1", "칭찬2"],
    "common_complaints": ["불만1", "불만2"],
    "hesitation_reasons": ["고민1", "고민2"]
  }},
  "selling_points": [
    {{"rank": 1, "point": "셀링포인트", "evidence": "근거"}}
  ],
  "recommended_tone": "추천 톤앤매너 설명"
}}"""

    result = generate_json(prompt, SYSTEM_INSTRUCTION)

    # 저장
    output_path = OUTPUT_DIR / "research_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, ensure_ascii=False, indent=2, fp=f)

    print(f"완료: {output_path}")
    print(f"경쟁사 {len(result.get('competitors', []))}개 분석")
    print(f"셀링포인트 {len(result.get('selling_points', []))}개 도출")


if __name__ == "__main__":
    main()
