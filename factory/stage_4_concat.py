"""factory/stage_4_concat.py — Stage 4: ffmpeg concat + BGM mixing + logo overlay."""

import os
import shutil
import subprocess
import tempfile

import requests

from factory._shared import (
    DEFAULT_BGM, EXPORTS_DIR, MUSIC_DIR, update_status,
)

_FFMPEG = os.path.abspath("ffmpeg.exe") if os.path.exists("ffmpeg.exe") else "ffmpeg"


def _run_ff(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [_FFMPEG, *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def download_video(url: str, dest: str) -> bool:
    """Download a GCS video URL to dest path."""
    try:
        resp = requests.get(url, stream=True, timeout=30)
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(65536):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Download failed {url}: {e}")
        return False


def pick_bgm(mood: str) -> str:
    """Select BGM file based on mood, fallback to DEFAULT_BGM."""
    mood_map = {
        "action": "action", "drama": "drama", "comedy": "comedy",
        "horror": "horror", "romance": "romance",
    }
    mood_key = mood_map.get(mood.lower(), "")
    if mood_key:
        for ext in (".mp3", ".wav", ".m4a"):
            candidate = os.path.join(MUSIC_DIR, f"{mood_key}{ext}")
            if os.path.exists(candidate):
                return candidate
    return DEFAULT_BGM if os.path.exists(DEFAULT_BGM) else ""


def concat_scenes(
    slug: str,
    scenes: list[dict],
    mood: str,
    orientation: str = "HORIZONTAL",
    tts_file: str | None = None,
) -> str | None:
    """Download scene videos, normalize, concat with BGM. Returns output path or None."""
    update_status(60, "Ghép Video", f"Đang tải {len(scenes)} cảnh về máy...")

    out_dir = os.path.join(EXPORTS_DIR, slug)
    os.makedirs(out_dir, exist_ok=True)

    prefix = orientation.lower()
    with tempfile.TemporaryDirectory() as tmp:
        normalized: list[str] = []
        for i, scene in enumerate(scenes):
            url = scene.get(f"{prefix}_video_url") or scene.get("vertical_video_url", "")
            if not url:
                continue
            raw = os.path.join(tmp, f"raw_{i:04d}.mp4")
            norm = os.path.join(tmp, f"norm_{i:04d}.mp4")
            if not download_video(url, raw):
                continue
            # Normalize: scale, fps=24, loudnorm
            _run_ff(
                "-y", "-i", raw,
                "-vf", "scale=1920:1080" if orientation == "HORIZONTAL" else "scale=1080:1920",
                "-r", "24", "-c:v", "libx264", "-preset", "fast",
                "-af", "loudnorm", "-c:a", "aac", "-b:a", "192k",
                norm,
            )
            if os.path.exists(norm):
                normalized.append(norm)

        if not normalized:
            return None

        update_status(75, "Ghép Video", f"Đang nối {len(normalized)} cảnh...")
        # Write concat list
        concat_list = os.path.join(tmp, "concat.txt")
        with open(concat_list, "w") as f:
            for p in normalized:
                f.write(f"file '{p}'\n")

        concat_out = os.path.join(tmp, "concat.mp4")
        _run_ff("-y", "-f", "concat", "-safe", "0", "-i", concat_list,
                "-c", "copy", concat_out)

        # Mix BGM
        bgm = pick_bgm(mood)
        mixed_out = os.path.join(tmp, "mixed.mp4")
        if bgm and os.path.exists(bgm):
            _run_ff(
                "-y", "-i", concat_out, "-stream_loop", "-1", "-i", bgm,
                "-filter_complex", "[1:a]volume=0.15[bgm];[0:a][bgm]amix=inputs=2:duration=first[aout]",
                "-map", "0:v", "-map", "[aout]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-shortest", mixed_out,
            )
        else:
            shutil.copy(concat_out, mixed_out)

        # TTS narration overlay
        if tts_file and os.path.exists(tts_file):
            tts_out = os.path.join(tmp, "tts_mixed.mp4")
            _run_ff(
                "-y", "-i", mixed_out, "-i", tts_file,
                "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:weights=1 3[aout]",
                "-map", "0:v", "-map", "[aout]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                tts_out,
            )
            if os.path.exists(tts_out):
                mixed_out = tts_out

        final_path = os.path.join(out_dir, f"{slug}_final.mp4")
        shutil.copy(mixed_out, final_path)

    update_status(85, "Ghép Xong", f"✅ {slug}_final.mp4 sẵn sàng upload")
    return final_path
