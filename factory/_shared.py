"""factory/_shared.py — Shared constants, config, and utility functions.

All pipeline stages import from here to avoid duplication.
"""

import json
import logging
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger("AutoFactory")

# ─── Directory Constants ───────────────────────────────────────
CONFIG_DIR = "./config"
API_KEYS_FILE = os.path.join(CONFIG_DIR, "api_keys.txt")
MUSIC_DIR = os.path.join(CONFIG_DIR, "music")
DEFAULT_BGM = os.path.join(CONFIG_DIR, "bgm.mp3")
STATUS_FILE = os.path.join(CONFIG_DIR, "status.json")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")
CHARACTERS_FILE = os.path.join(CONFIG_DIR, "characters.json")
LOGO_FILE = os.path.join(CONFIG_DIR, "brand_logo.png")

DIR_1 = "./1_nhap_lieu"
DIR_2 = "./2_cho_duyet"
DIR_3 = "./3_dang_render_anh"
DIR_3_5 = "./3.5_cho_duyet_anh"
DIR_3_8 = "./3.8_dang_dung_video"
DIR_4 = "./4_hoan_thanh"
EXPORTS_DIR = "./exports"

API_URL = "http://127.0.0.1:8100/api"
DEFAULT_ORIENTATION = "HORIZONTAL"


@dataclass
class FactoryConfig:
    """Runtime configuration for the pipeline."""
    api_url: str = API_URL
    orientation: str = DEFAULT_ORIENTATION
    api_keys: list[str] = field(default_factory=list)
    current_key_idx: int = 0
    status_file: str = STATUS_FILE
    settings_file: str = SETTINGS_FILE
    characters_file: str = CHARACTERS_FILE
    logo_file: str = LOGO_FILE
    bgm_dir: str = MUSIC_DIR
    default_bgm: str = DEFAULT_BGM
    exports_dir: str = EXPORTS_DIR


def ensure_directories() -> None:
    """Create required pipeline directories."""
    for d in [CONFIG_DIR, MUSIC_DIR, DIR_1, DIR_2, DIR_3, DIR_3_5, DIR_3_8, DIR_4, EXPORTS_DIR]:
        os.makedirs(d, exist_ok=True)


def check_ffmpeg() -> None:
    """Abort with clear message if ffmpeg is not found."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except Exception:
        print("\n[BÁO ĐỘNG ĐỎ] KHÔNG TÌM THẤY FFMPEG!")
        print("Hệ thống không thể nối video nếu thiếu FFmpeg.")
        sys.exit(1)


def load_api_keys() -> list[str]:
    """Load Gemini API keys from config file."""
    if not os.path.exists(API_KEYS_FILE):
        Path(API_KEYS_FILE).write_text("YOUR_GEMINI_API_KEY_HERE\n", encoding="utf-8")
    keys: list[str] = []
    with open(API_KEYS_FILE, encoding="utf-8") as f:
        for line in f:
            key = line.strip()
            if key and not key.startswith("#"):
                keys.append(key)
    return keys


def update_status(progress: int, phase: str, log_msg: str) -> None:
    """Write pipeline status to status.json for the dashboard."""
    logger.info("[%d%%] %s: %s", progress, phase, log_msg)
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump({"progress": progress, "phase": phase, "log": log_msg}, f, ensure_ascii=False)
    except Exception as e:
        logger.warning("Status write failed: %s", e)


def is_night_mode_active() -> bool:
    """Return True if night mode is enabled in settings.json."""
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            return json.load(f).get("night_mode", False)
    except Exception:
        return False
