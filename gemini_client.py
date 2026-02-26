"""
Gemini 2.5 Pro 클라이언트
.env에서 GEMINI_API_KEY를 읽어 사용합니다.
"""

import os
import json
from pathlib import Path

# .env 파일에서 API 키 로드
ENV_PATH = Path(__file__).parent.parent / ".env"


def load_api_key():
    """Load GEMINI_API_KEY from .env file or environment"""
    # 환경변수 우선
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key

    # .env 파일에서 읽기
    if ENV_PATH.exists():
        with open(ENV_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("GEMINI_API_KEY="):
                    return line.split("=", 1)[1].strip()

    raise ValueError(
        f"GEMINI_API_KEY를 찾을 수 없습니다.\n"
        f".env 파일 경로: {ENV_PATH}\n"
        f"GEMINI_API_KEY=your_key 형식으로 입력하세요."
    )


def create_client():
    """Gemini API 클라이언트 생성"""
    from google import genai

    api_key = load_api_key()
    return genai.Client(api_key=api_key)


def generate_text(prompt, system_instruction=None, temperature=0.7):
    """
    Gemini 2.5 Pro로 텍스트 생성

    Args:
        prompt: 사용자 프롬프트
        system_instruction: 시스템 지시사항
        temperature: 창의성 조절 (0.0~1.0)

    Returns:
        생성된 텍스트 (str)
    """
    from google.genai import types

    client = create_client()

    config = types.GenerateContentConfig(
        temperature=temperature,
    )
    if system_instruction:
        config.system_instruction = system_instruction

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config,
    )

    return response.text


def generate_json(prompt, system_instruction=None, temperature=0.3):
    """
    Gemini 2.5 Pro로 JSON 생성 (파싱까지 처리)

    Args:
        prompt: 사용자 프롬프트
        system_instruction: 시스템 지시사항
        temperature: 낮을수록 일관된 출력

    Returns:
        파싱된 dict/list
    """
    from google.genai import types

    client = create_client()

    config = types.GenerateContentConfig(
        temperature=temperature,
        response_mime_type="application/json",
    )
    if system_instruction:
        config.system_instruction = system_instruction

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config,
    )

    return json.loads(response.text)
