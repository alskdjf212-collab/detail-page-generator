#!/usr/bin/env python3
"""
상세페이지 PNG 렌더러
output/render_data.json을 읽어서 10개 섹션 PNG를 생성하고
하나의 긴 이미지로 합칩니다.
"""

import json
import os
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# 프로젝트 루트
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
RENDER_DATA = OUTPUT_DIR / "render_data.json"
PRODUCT_PHOTO = OUTPUT_DIR / "product_photo.png"
PHOTO_SCENE = OUTPUT_DIR / "photo_scene.jpg"
PHOTO_LIFESTYLE = OUTPUT_DIR / "photo_lifestyle.jpg"
PHOTO_NATURE = OUTPUT_DIR / "photo_nature.jpg"

# macOS 한국어 폰트
FONT_PATHS = [
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
]

# 이모지 → 텍스트 심볼 매핑
EMOJI_MAP = {
    "🏋️": "●",
    "🏋": "●",
    "🪶": "◆",
    "🛡️": "■",
    "🛡": "■",
    "🎒": "▲",
    "🧵": "◇",
    "⚡": "▶",
    "💡": "★",
    "🔧": "◈",
    "✅": "✓",
    "❌": "✕",
    "⭐": "★",
    "🌟": "★",
    "📦": "□",
    "🏕️": "▲",
    "🏕": "▲",
    "🪑": "◆",
    "💪": "●",
    "🎯": "◎",
    "👍": "●",
    "👎": "●",
    "🔥": "★",
    "❤️": "♥",
    "❤": "♥",
    "😊": "",
    "😢": "",
    "🤔": "",
    "📱": "■",
    "🚗": "▶",
    "⚖️": "◆",
    "⚖": "◆",
    "🔒": "■",
    "💰": "◆",
    "🏆": "★",
    "📐": "◇",
    "🧳": "□",
    "🪄": "◆",
    "♻️": "◇",
    "🌿": "◇",
    "☀️": "○",
    "🌙": "●",
    "⛺": "▲",
    "🔩": "●",
    "🪨": "■",
    "🧲": "◆",
    "✨": "★",
}


def clean_emoji(text):
    """이모지를 렌더링 가능한 심볼로 대체"""
    if not text:
        return text
    for emoji, symbol in EMOJI_MAP.items():
        text = text.replace(emoji, symbol)
    # 남은 이모지 패턴 제거 (variation selector 등)
    text = re.sub(r'[\ufe0f\u200d]', '', text)
    # 기타 남은 이모지 → ● 로 대체
    cleaned = []
    for ch in text:
        cp = ord(ch)
        if (0x1F600 <= cp <= 0x1F9FF or  # emoticons, symbols
            0x2600 <= cp <= 0x27BF or     # misc symbols
            0x1F300 <= cp <= 0x1F5FF or   # misc symbols and pictographs
            0x1FA00 <= cp <= 0x1FA6F or   # chess, extended-A
            0x1FA70 <= cp <= 0x1FAFF or   # symbols extended-A
            0xFE00 <= cp <= 0xFE0F):      # variation selectors
            cleaned.append("●")
        else:
            cleaned.append(ch)
    result = ''.join(cleaned)
    # 연속 ● 정리
    result = re.sub(r'●{2,}', '●', result)
    return result


def find_font():
    """사용 가능한 한국어 폰트 찾기"""
    for path in FONT_PATHS:
        if os.path.exists(path):
            return path
    print("WARNING: 한국어 폰트를 찾을 수 없습니다.")
    return None


FONT_PATH = find_font()


def get_font(size, weight="normal"):
    """폰트 로드"""
    if not FONT_PATH:
        return ImageFont.load_default()
    try:
        if weight == "bold" and FONT_PATH.endswith(".ttc"):
            try:
                return ImageFont.truetype(FONT_PATH, size, index=5)
            except Exception:
                return ImageFont.truetype(FONT_PATH, size, index=0)
        return ImageFont.truetype(FONT_PATH, size, index=0)
    except Exception:
        return ImageFont.load_default()


def wrap_text(text, font, max_width, draw):
    """텍스트를 max_width에 맞게 줄바꿈"""
    if not max_width or max_width <= 0:
        return [text]

    lines = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue

        current_line = ""
        for char in paragraph:
            test_line = current_line + char
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] > max_width and current_line:
                lines.append(current_line)
                current_line = char
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)

    return lines


def draw_text_element(draw, elem, canvas_width):
    """텍스트 요소 렌더링"""
    content = clean_emoji(elem.get("content", ""))
    if not content:
        return

    font_size = elem.get("font_size", 24)
    font_weight = elem.get("font_weight", "normal")
    color = elem.get("color", "#333333")
    align = elem.get("align", "left")
    x = elem.get("x", 60)
    y = elem.get("y", 0)
    max_width = elem.get("max_width", canvas_width - 120)

    font = get_font(font_size, font_weight)
    lines = wrap_text(content, font, max_width, draw)

    line_height = int(font_size * 1.5)

    for i, line in enumerate(lines):
        line_y = y + i * line_height
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]

        if align == "center":
            line_x = x - text_width // 2
        elif align == "right":
            line_x = x - text_width
        else:
            line_x = x

        draw.text((line_x, line_y), line, fill=color, font=font)


def draw_rectangle(draw, elem):
    """사각형 요소 렌더링"""
    x = elem.get("x", 0)
    y = elem.get("y", 0)
    w = elem.get("width", 100)
    h = elem.get("height", 100)
    fill = elem.get("fill", None)
    radius = elem.get("radius", 0)
    outline = elem.get("outline", None)
    outline_width = elem.get("outline_width", 1)

    if radius > 0:
        draw.rounded_rectangle(
            [x, y, x + w, y + h],
            radius=radius,
            fill=fill,
            outline=outline,
            width=outline_width,
        )
    else:
        draw.rectangle(
            [x, y, x + w, y + h],
            fill=fill,
            outline=outline,
            width=outline_width,
        )


def draw_line(draw, elem):
    """선 요소 렌더링"""
    x1 = elem.get("x1", 0)
    y1 = elem.get("y1", 0)
    x2 = elem.get("x2", 100)
    y2 = elem.get("y2", 0)
    color = elem.get("color", "#CCCCCC")
    width = elem.get("width", 1)

    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)


def draw_badge(draw, elem):
    """배지 요소 렌더링"""
    content = clean_emoji(elem.get("content", ""))
    if not content:
        return

    x = elem.get("x", 0)
    y = elem.get("y", 0)
    bg_color = elem.get("bg_color", "#FF4444")
    text_color = elem.get("text_color", "#FFFFFF")
    font_size = elem.get("font_size", 20)
    padding = elem.get("padding", 12)

    font = get_font(font_size, "bold")
    bbox = draw.textbbox((0, 0), content, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    draw.rounded_rectangle(
        [x, y, x + text_w + padding * 2, y + text_h + padding * 2],
        radius=8,
        fill=bg_color,
    )
    draw.text((x + padding, y + padding), content, fill=text_color, font=font)


def draw_circle(draw, elem):
    """원형 요소 렌더링"""
    cx = elem.get("cx", 50)
    cy = elem.get("cy", 50)
    radius = elem.get("radius", 25)
    fill = elem.get("fill", None)
    outline = elem.get("outline", None)

    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=fill,
        outline=outline,
    )


def draw_icon_text(draw, elem, canvas_width):
    """아이콘 + 텍스트 요소 렌더링 (이모지를 심볼로 대체)"""
    icon = clean_emoji(elem.get("icon", ""))
    label = clean_emoji(elem.get("label", ""))
    x = elem.get("x", 60)
    y = elem.get("y", 0)
    font_size = elem.get("font_size", 24)
    color = elem.get("color", "#333333")
    accent = elem.get("accent_color", "#2ECC71")

    font = get_font(font_size)
    bold_font = get_font(font_size, "bold")

    # 아이콘을 accent 색상 원으로 대체
    if icon:
        circle_r = font_size // 2 + 4
        draw.ellipse(
            [x, y - 2, x + circle_r * 2, y + circle_r * 2 - 2],
            fill=accent,
        )
        # 아이콘 심볼을 원 안에 흰색으로
        icon_font = get_font(font_size - 4, "bold")
        bbox = draw.textbbox((0, 0), icon, font=icon_font)
        iw = bbox[2] - bbox[0]
        ih = bbox[3] - bbox[1]
        draw.text(
            (x + circle_r - iw // 2, y + circle_r - ih // 2 - 2),
            icon, fill="#FFFFFF", font=icon_font,
        )
        draw.text((x + circle_r * 2 + 12, y + 4), label, fill=color, font=font)
    else:
        draw.text((x, y), label, fill=color, font=font)


def load_photo(path):
    """사진 로드 (RGBA 변환)"""
    if path.exists():
        return Image.open(path).convert("RGBA")
    return None


def fit_photo(photo, target_w, target_h):
    """사진을 target 크기에 맞게 crop+resize (비율 유지, 꽉 채움)"""
    pw, ph = photo.size
    target_ratio = target_w / target_h
    photo_ratio = pw / ph

    if photo_ratio > target_ratio:
        # 사진이 더 넓음 → 높이 맞추고 좌우 크롭
        new_h = ph
        new_w = int(ph * target_ratio)
        left = (pw - new_w) // 2
        photo = photo.crop((left, 0, left + new_w, new_h))
    else:
        # 사진이 더 높음 → 폭 맞추고 상하 크롭
        new_w = pw
        new_h = int(pw / target_ratio)
        top = (ph - new_h) // 2
        photo = photo.crop((0, top, new_w, top + new_h))

    return photo.resize((target_w, target_h), Image.LANCZOS)


def paste_product_photo(img, section_id, canvas_width, canvas_height):
    """제품 사진을 해당 섹션에 삽입"""
    product = load_photo(PRODUCT_PHOTO)
    scene = load_photo(PHOTO_SCENE)
    lifestyle = load_photo(PHOTO_LIFESTYLE)

    nature = load_photo(PHOTO_NATURE)
    person = load_photo(OUTPUT_DIR / "photo_person_chair.jpg")
    family = load_photo(OUTPUT_DIR / "photo_family.jpg")
    setup = load_photo(OUTPUT_DIR / "photo_setup.jpg")

    if section_id == "01_hero" and product:
        # 히어로: 우측 40%에 제품 사진
        target_h = int(canvas_height * 0.8)
        ratio = target_h / product.height
        target_w = int(product.width * ratio)
        if target_w > canvas_width * 0.4:
            target_w = int(canvas_width * 0.4)
            ratio = target_w / product.width
            target_h = int(product.height * ratio)
        resized = product.resize((target_w, target_h), Image.LANCZOS)
        x = canvas_width - target_w - 20
        y = (canvas_height - target_h) // 2
        img.paste(resized, (x, y), resized)

    elif section_id == "02_photo_banner" and person:
        # 사진 배너: 풀폭 사진 + 다크 오버레이
        resized = fit_photo(person, canvas_width, canvas_height)
        overlay = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 130))
        resized = Image.alpha_composite(resized, overlay)
        img.paste(resized, (0, 0), resized)

    elif section_id == "03_key_numbers" and scene:
        # 핵심 숫자: 배경에 살짝 씬 사진
        resized = fit_photo(scene, canvas_width, canvas_height)
        overlay = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 235))
        resized = Image.alpha_composite(resized, overlay)
        img.paste(resized, (0, 0), resized)

    elif section_id == "04_pain_solution" and product:
        # 고민/해결: 좌측 45%에 제품 사진
        target_h = int(canvas_height * 0.7)
        ratio = target_h / product.height
        target_w = int(product.width * ratio)
        if target_w > canvas_width * 0.42:
            target_w = int(canvas_width * 0.42)
            ratio = target_w / product.width
            target_h = int(product.height * ratio)
        resized = product.resize((target_w, target_h), Image.LANCZOS)
        x = 30
        y = (canvas_height - target_h) // 2 + 20
        img.paste(resized, (x, y), resized)

    elif section_id == "07_photo_lifestyle" and family:
        # 라이프스타일: 풀폭 사진 + 오버레이
        resized = fit_photo(family, canvas_width, canvas_height)
        overlay = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 110))
        resized = Image.alpha_composite(resized, overlay)
        img.paste(resized, (0, 0), resized)

    elif section_id == "09_reviews" and nature:
        # 후기: 자연 배경 + 강한 오버레이
        resized = fit_photo(nature, canvas_width, canvas_height)
        overlay = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 210))
        resized = Image.alpha_composite(resized, overlay)
        img.paste(resized, (0, 0), resized)

    elif section_id == "10_cta" and product:
        # CTA: 우측에 제품
        target_h = int(canvas_height * 0.65)
        ratio = target_h / product.height
        target_w = int(product.width * ratio)
        resized = product.resize((target_w, target_h), Image.LANCZOS)
        x = canvas_width - target_w - 30
        y = (canvas_height - target_h) // 2
        img.paste(resized, (x, y), resized)

    return img


def render_section(section_data):
    """단일 섹션 PNG 렌더링"""
    canvas = section_data.get("canvas", {"width": 1080, "height": 800})
    width = canvas.get("width", 1080)
    height = canvas.get("height", 800)
    bg_color = section_data.get("background", "#FFFFFF")
    section_id = section_data.get("id", "")

    # RGBA 캔버스 (사진 합성 위해)
    img = Image.new("RGBA", (width, height), bg_color)

    # 1단계: 사진을 먼저 삽입 (텍스트 뒤에 깔림)
    img = paste_product_photo(img, section_id, width, height)

    # 2단계: 요소를 사진 위에 렌더링
    draw = ImageDraw.Draw(img)
    elements = section_data.get("elements", [])
    for elem in elements:
        elem_type = elem.get("type", "")

        if elem_type == "text":
            draw_text_element(draw, elem, width)
        elif elem_type == "rectangle":
            draw_rectangle(draw, elem)
        elif elem_type == "line":
            draw_line(draw, elem)
        elif elem_type == "badge":
            draw_badge(draw, elem)
        elif elem_type == "circle":
            draw_circle(draw, elem)
        elif elem_type == "icon_text":
            draw_icon_text(draw, elem, width)
        else:
            print(f"  [SKIP] 알 수 없는 요소 타입: {elem_type}")

    # RGB로 변환
    return img.convert("RGB")


def merge_sections(section_images):
    """모든 섹션을 하나의 긴 이미지로 합치기"""
    if not section_images:
        return None

    total_width = max(img.width for img in section_images)
    total_height = sum(img.height for img in section_images)

    merged = Image.new("RGB", (total_width, total_height), "#FFFFFF")

    y_offset = 0
    for img in section_images:
        # 폭이 다른 경우 중앙 정렬
        x_offset = (total_width - img.width) // 2
        merged.paste(img, (x_offset, y_offset))
        y_offset += img.height

    return merged


def main():
    if not RENDER_DATA.exists():
        print(f"ERROR: {RENDER_DATA} 파일이 없습니다.")
        sys.exit(1)

    with open(RENDER_DATA, "r", encoding="utf-8") as f:
        data = json.load(f)

    sections = data.get("sections", [])
    if not sections:
        print("ERROR: render_data.json에 섹션 데이터가 없습니다.")
        sys.exit(1)

    photo_status = "있음" if PRODUCT_PHOTO.exists() else "없음"

    print(f"\n{'='*50}")
    print(f"  상세페이지 PNG 렌더링 시작")
    print(f"  섹션 수: {len(sections)}")
    print(f"  제품 사진: {photo_status}")
    print(f"  출력 폴더: {OUTPUT_DIR}")
    print(f"{'='*50}\n")

    section_images = []
    generated = []

    for section in sections:
        section_id = section.get("id", "unknown")
        filename = section.get("filename", f"{section_id}.png")
        output_path = OUTPUT_DIR / filename

        print(f"  렌더링: {filename} ... ", end="")

        try:
            img = render_section(section)
            img.save(output_path, "PNG", quality=95)
            print(f"OK ({img.width}x{img.height})")
            generated.append(str(output_path))
            section_images.append(img)
        except Exception as e:
            print(f"FAILED ({e})")

    # 하나의 긴 이미지로 합치기
    print(f"\n  합치기: detail_page_full.png ... ", end="")
    try:
        merged = merge_sections(section_images)
        if merged:
            merged_path = OUTPUT_DIR / "detail_page_full.png"
            merged.save(merged_path, "PNG", quality=95)
            print(f"OK ({merged.width}x{merged.height})")
            generated.append(str(merged_path))
    except Exception as e:
        print(f"FAILED ({e})")

    print(f"\n{'='*50}")
    print(f"  완료: {len(generated)} 파일 생성")
    print(f"{'='*50}\n")

    for path in generated:
        print(f"  -> {path}")

    print()


if __name__ == "__main__":
    main()
