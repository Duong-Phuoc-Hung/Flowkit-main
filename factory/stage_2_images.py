"""factory/stage_2_images.py — Stage 2: Reference + Scene Image Generation."""

import json
import os
import shutil
import traceback
from typing import Any

import requests

from factory._shared import (
    DIR_3, DIR_3_8, update_status, is_night_mode_active, API_URL,
    DEFAULT_ORIENTATION, CHARACTERS_FILE,
)

try:
    import flowkit.api_client as _api
except ImportError:
    _api = None  # type: ignore[assignment]


def _api_post(path: str, **kwargs) -> Any:
    if _api:
        return _api.post(f"{API_URL}{path}", **kwargs)
    return requests.post(f"{API_URL}{path}", **kwargs)


def _poll_batch(target_id: str, req_type: str, max_retries: int = 3) -> bool:
    """Poll batch status until done=True or max_retries exceeded."""
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
    try:
        from batch_poll import poll_batch
        return poll_batch(target_id, req_type, max_retries=max_retries)
    except ImportError:
        return False


def generate_ref_images(project_id: str, entities: list[dict], orientation: str = "PORTRAIT") -> None:
    """Submit batch request to generate reference images for all entities."""
    update_status(12, "Vẽ Ảnh Tham Chiếu", f"Đang vẽ {len(entities)} thực thể...")
    requests_payload = [
        {
            "type": "GENERATE_CHARACTER_IMAGE",
            "project_id": project_id,
            "character_id": e["id"],
            "orientation": orientation,
        }
        for e in entities
    ]
    requests.post(f"{API_URL}/requests/batch", json={"requests": requests_payload})


def generate_scene_images(
    video_id: str,
    project_id: str,
    scenes: list[dict],
    orientation: str = "HORIZONTAL",
) -> bool:
    """Submit batch request to generate scene images with 3 smart retry rescue attempts."""
    update_status(20, "Vẽ Ảnh Cảnh", f"Đang vẽ {len(scenes)} cảnh...")
    batch = [
        {
            "type": "GENERATE_IMAGE",
            "scene_id": s["id"],
            "project_id": project_id,
            "video_id": video_id,
            "orientation": orientation,
        }
        for s in scenes
    ]
    requests.post(f"{API_URL}/requests/batch", json={"requests": batch})

    for attempt in range(3):
        success = _poll_batch(video_id, "GENERATE_IMAGE", max_retries=2)
        if success:
            return True

        final_scenes = requests.get(f"{API_URL}/scenes?video_id={video_id}").json()
        failed_scenes = [s for s in final_scenes if s.get(f"{orientation.lower()}_image_status") == "FAILED"]
        if not failed_scenes:
            return True  # network timeout — consider success

        update_status(35, "Tự Động Cứu Hộ", f"Phát hiện {len(failed_scenes)} ảnh bị lỗi. Đang vẽ lại (lần {attempt + 1}/3)...")
        requests.post(f"{API_URL}/requests/batch", json={
            "requests": [
                {
                    "type": "REGENERATE_IMAGE",
                    "video_id": video_id,
                    "scene_id": s["id"],
                    "project_id": project_id,
                    "orientation": orientation,
                }
                for s in failed_scenes
            ]
        })

    return False


def process_render_images() -> None:
    """Main loop: process scripts from DIR_3 → DIR_3_8."""
    if is_night_mode_active():
        return

    files = [f for f in os.listdir(DIR_3) if f.lower().endswith(".json")]
    for filename in files:
        slug = filename.replace(".json", "")
        path = os.path.join(DIR_3, filename)
        p_id = None
        try:
            with open(path, encoding="utf-8") as f:
                script_data = json.load(f)

            p_id = script_data.get("project_id")
            v_id = script_data.get("video_id")
            created_scenes = script_data.get("created_scenes", [])

            # Create project, video, and scenes if not already in DB
            if not p_id:
                update_status(15, "Đang Khởi Tạo Project", f"Đẩy {slug} lên máy chủ...")
                res_p = requests.post(f"{API_URL}/projects", json={
                    "name": slug,
                    "story": script_data.get("story", ""),
                    "material": "3d_pixar",
                    "characters": script_data.get("characters", []),
                }).json()
                p_id = res_p.get("id")
                if not p_id:
                    continue

                # Character face cloning
                try:
                    with open(CHARACTERS_FILE, encoding="utf-8") as cf:
                        cloned_chars = json.load(cf)
                    chars_in_proj = requests.get(f"{API_URL}/projects/{p_id}/characters").json()
                    for c in chars_in_proj:
                        c_name = c.get("name", "")
                        if c_name in cloned_chars:
                            requests.patch(f"{API_URL}/characters/{c['id']}", json={"media_id": cloned_chars[c_name]})
                except Exception as e:
                    print(f"Warning character clone: {e}")

                res_v = requests.post(f"{API_URL}/videos", json={
                    "project_id": p_id, "title": slug, "display_order": 0,
                }).json()
                v_id = res_v.get("id")

                created_scenes = []
                for i, scene in enumerate(script_data.get("scenes", [])):
                    payload = {
                        "video_id": v_id,
                        "display_order": i,
                        "prompt": scene.get("prompt", ""),
                        "video_prompt": scene.get("video_prompt", ""),
                        "narrator_text": scene.get("narrator_text", ""),
                        "character_names": scene.get("character_names", []),
                        "chain_type": "ROOT" if i == 0 else "CONTINUATION",
                    }
                    if created_scenes:
                        payload["parent_scene_id"] = created_scenes[-1]["id"]
                    s_res = requests.post(f"{API_URL}/scenes", json=payload)
                    if s_res.status_code == 200:
                        s_obj = s_res.json()
                        s_obj["voice_gender"] = scene.get("voice_gender", "Nữ")
                        created_scenes.append(s_obj)

                # Character ref images if needed
                chars_for_ref = requests.get(f"{API_URL}/projects/{p_id}/characters").json()
                char_reqs = [
                    {"type": "GENERATE_CHARACTER_IMAGE", "project_id": p_id, "character_id": c["id"], "video_id": v_id}
                    for c in chars_for_ref if not c.get("media_id")
                ]
                if char_reqs:
                    requests.post(f"{API_URL}/requests/batch", json={"requests": char_reqs})
                    _poll_batch(p_id, "GENERATE_CHARACTER_IMAGE", max_retries=2)

            success = generate_scene_images(v_id, p_id, created_scenes, DEFAULT_ORIENTATION)
            if not success:
                raise Exception("Lỗi khi vẽ ảnh tĩnh (Đã tự động cứu hộ 3 lần nhưng không thành công)")

            script_data.update({"project_id": p_id, "video_id": v_id, "created_scenes": created_scenes})
            with open(path, "w", encoding="utf-8") as f:
                json.dump(script_data, f, ensure_ascii=False, indent=2)

            shutil.move(path, os.path.join(DIR_3_8, filename))
            update_status(43, "Tạo Ảnh Hoàn Tất", f"✅ {slug} đã vẽ xong ảnh, chuyển sang Dựng Video!")

        except Exception as e:
            traceback.print_exc()
            update_status(0, "LỖI Ảnh", str(e))
            if p_id:
                try:
                    requests.delete(f"{API_URL}/projects/{p_id}")
                except Exception:
                    pass
            err_dir = os.path.abspath("99_bao_loi")
            os.makedirs(err_dir, exist_ok=True)
            try:
                shutil.move(path, os.path.join(err_dir, filename))
            except Exception:
                pass
