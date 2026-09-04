"""factory/stage_1_script.py — Stage 1: AI Script Generation via Gemini."""

import json
import os
import shutil
import time

import google.generativeai as genai

from factory._shared import (
    DIR_1, DIR_2, DIR_3, update_status, is_night_mode_active,
    CHARACTERS_FILE,
)

_API_KEYS: list[str] = []
_current_key_idx = 0


def _config_gemini() -> None:
    if _API_KEYS:
        genai.configure(api_key=_API_KEYS[_current_key_idx])


def init(api_keys: list[str]) -> None:
    """Initialize with loaded API keys."""
    global _API_KEYS, _current_key_idx
    _API_KEYS = api_keys
    _current_key_idx = 0
    _config_gemini()


def _rotate_key() -> None:
    global _current_key_idx
    if len(_API_KEYS) > 1:
        _current_key_idx = (_current_key_idx + 1) % len(_API_KEYS)
        update_status(5, "Lỗi Quota", f"🔄 Đổi sang Key số {_current_key_idx + 1}")
        _config_gemini()
    else:
        time.sleep(30)


def generate_script(idea: str, proj_name: str, fact_check: bool = False) -> dict | None:
    """Call Gemini to generate a structured scene script from a raw idea.

    Returns parsed JSON dict or None on failure.
    """
    update_status(5, "Đang Tạo Kịch Bản", f"AI đang phân tích ý tưởng: {idea[:60]}...")

    # Load character references
    characters: dict = {}
    try:
        with open(CHARACTERS_FILE, encoding="utf-8") as f:
            characters = json.load(f)
    except Exception:
        pass

    char_context = json.dumps(characters, ensure_ascii=False) if characters else "{}"

    prompt = f"""Bạn là chuyên gia viết kịch bản video AI.
Ý tưởng: {idea}
Nhân vật tham chiếu: {char_context}
Fact-check trước khi viết: {fact_check}

Trả về JSON hợp lệ với cấu trúc:
{{
  "title": "...",
  "mood": "action|drama|comedy|horror|romance",
  "scenes": [
    {{
      "prompt": "Mô tả hành động cảnh (không mô tả ngoại hình nhân vật)",
      "video_prompt": "0-3s: ... 3-6s: ... 6-8s: ...",
      "narrator_text": "Lời dẫn chuyện...",
      "character_names": ["Tên nhân vật"]
    }}
  ]
}}
Tạo 8-12 cảnh. Chỉ trả về JSON thuần, không markdown."""

    for attempt in range(6):
        try:
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            response = model.generate_content(prompt)
            text = response.text.strip()
            # Strip markdown fences if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text.strip())
        except Exception:
            _rotate_key()
            if attempt == 5:
                update_status(0, "LỖI", "Không thể tạo kịch bản sau 6 lần thử.")
                return None
    return None


def process_input_stories() -> None:
    """Main loop: process JSON idea files from DIR_1 → DIR_2/DIR_3."""
    if is_night_mode_active():
        return

    files = [f for f in os.listdir(DIR_1) if f.lower().endswith(".json")]
    for filename in files:
        path = os.path.join(DIR_1, filename)
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            idea = data.get("idea", "")
            proj_name = data.get("projName", filename.replace(".json", ""))
            fact_check = data.get("factCheck", False)

            if not idea:
                shutil.move(path, os.path.join(DIR_2, filename))
                continue

            script = generate_script(idea, proj_name, fact_check)
            if script:
                out_path = os.path.join(DIR_3, filename)
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(script, f, ensure_ascii=False, indent=2)
                os.remove(path)
                update_status(10, "Kịch Bản Xong", f"✅ {proj_name} sẵn sàng vẽ ảnh")
        except Exception as e:
            update_status(0, "LỖI Script", str(e))
