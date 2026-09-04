"""factory/stage_3_videos.py — Stage 3: AI Video Rendering."""

import json
import os
import shutil

import requests

from factory._shared import (
    DIR_3_8, DIR_4, update_status, is_night_mode_active, API_URL,
)


def _poll_batch(video_id: str, req_type: str, max_retries: int = 3) -> bool:
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
    try:
        from batch_poll import poll_batch
        return poll_batch(video_id, req_type, max_retries=max_retries)
    except ImportError:
        return False


def generate_videos(
    video_id: str,
    project_id: str,
    scenes: list[dict],
    orientation: str = "HORIZONTAL",
) -> bool:
    """Submit batch video requests with smart retry (3 attempts)."""
    update_status(45, "Đang Dựng Video", "Bắt đầu chuyển động hóa AI...")
    batch = [
        {
            "type": "GENERATE_VIDEO",
            "scene_id": s["id"],
            "project_id": project_id,
            "video_id": video_id,
            "orientation": orientation,
        }
        for s in scenes
    ]
    requests.post(f"{API_URL}/requests/batch", json={"requests": batch})

    for attempt in range(3):
        success = _poll_batch(video_id, "GENERATE_VIDEO", max_retries=2)
        if success:
            return True

        # Smart retry: only re-submit failed scenes
        final = requests.get(f"{API_URL}/scenes?video_id={video_id}").json()
        key = f"{orientation.lower()}_video_status"
        failed = [s for s in final if s.get(key) == "FAILED"]
        if not failed:
            return True  # network timeout — consider success

        update_status(46, "Cứu Hộ Video",
                      f"Phát hiện {len(failed)} video lỗi. Render lại (lần {attempt + 1}/3)...")
        regen_batch = [
            {
                "type": "REGENERATE_VIDEO",
                "scene_id": s["id"],
                "project_id": project_id,
                "video_id": video_id,
                "orientation": orientation,
            }
            for s in failed
        ]
        requests.post(f"{API_URL}/requests/batch", json={"requests": regen_batch})

    return False


def process_render_video() -> None:
    """Main loop: process approved scenes from DIR_3_8 → DIR_4."""
    if is_night_mode_active():
        return

    files = [f for f in os.listdir(DIR_3_8) if f.lower().endswith(".json")]
    for filename in files:
        path = os.path.join(DIR_3_8, filename)
        slug = filename.replace(".json", "")
        try:
            with open(path, encoding="utf-8") as f:
                script_data = json.load(f)

            v_id = script_data.get("video_id")
            p_id = script_data.get("project_id")
            scenes = script_data.get("created_scenes", [])

            if not (v_id and p_id and scenes):
                continue

            from factory._shared import DEFAULT_ORIENTATION
            success = generate_videos(v_id, p_id, scenes, DEFAULT_ORIENTATION)
            if not success:
                raise RuntimeError("Video rendering failed after 3 rescue attempts")

            # Refresh URLs before concat
            update_status(46, "Làm Mới Dữ Liệu", "Gia hạn đường link GCS...")
            try:
                requests.post(f"{API_URL}/flow/refresh-urls/{p_id}", timeout=15)
            except Exception as e:
                print(f"Refresh URL warning: {e}")

            shutil.move(path, os.path.join(DIR_4, filename))
            update_status(50, "Video Hoàn Tất", f"✅ {slug} sẵn sàng ghép video")

        except Exception as e:
            update_status(0, "LỖI Video", str(e))
            err_dir = os.path.abspath("99_bao_loi")
            os.makedirs(err_dir, exist_ok=True)
            try:
                shutil.move(path, os.path.join(err_dir, filename))
            except Exception:
                pass
