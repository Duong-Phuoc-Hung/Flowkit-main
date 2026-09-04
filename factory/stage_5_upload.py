"""factory/stage_5_upload.py — Stage 5: YouTube Upload."""

import os
import subprocess

from factory._shared import EXPORTS_DIR, update_status


def _find_video(slug: str) -> str | None:
    out_dir = os.path.join(EXPORTS_DIR, slug)
    if not os.path.isdir(out_dir):
        return None
    for fname in os.listdir(out_dir):
        if fname.endswith("_final.mp4") or fname.endswith(".mp4"):
            return os.path.join(out_dir, fname)
    return None


def upload_to_youtube(
    slug: str,
    title: str,
    description: str = "",
    tags: str = "",
    privacy: str = "unlisted",
    channel_id: str | None = None,
) -> bool:
    """Upload the final video for a slug to YouTube via yt-dlp or google-api.

    Returns True on success, False on failure.
    Actual upload logic delegates to existing scripts/youtube_upload.py if present.
    """
    video_path = _find_video(slug)
    if not video_path or not os.path.exists(video_path):
        update_status(0, "LỖI Upload", f"Không tìm thấy video cho: {slug}")
        return False

    update_status(90, "Đang Upload", f"🚀 Đang đẩy {slug} lên YouTube...")

    # Delegate to existing upload script if present
    upload_script = os.path.abspath(os.path.join("scripts", "youtube_upload.py"))
    if os.path.exists(upload_script):
        try:
            result = subprocess.run(
                ["python", upload_script,
                 "--file", video_path,
                 "--title", title,
                 "--description", description,
                 "--tags", tags,
                 "--privacy", privacy,
                 *(["--channel-id", channel_id] if channel_id else [])],
                capture_output=True, text=True, timeout=600,
            )
            if result.returncode == 0:
                update_status(100, "Đã Upload", f"✅ {slug} đã lên YouTube!")
                return True
            else:
                update_status(0, "LỖI Upload", result.stderr[:200])
                return False
        except subprocess.CalledProcessError as e:
            update_status(0, "LỖI Upload", str(e))
            return False
        except Exception as e:
            update_status(0, "LỖI Upload", str(e))
            return False
    else:
        # Fallback: log path for manual upload
        update_status(95, "Cần Upload Thủ Công",
                      f"Video sẵn sàng tại: {video_path}")
        return True
