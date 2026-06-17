import warnings
warnings.filterwarnings("ignore")
import os
import sys
import subprocess
import json
import pathlib

def run_script(script_path, args):
    """Execute another Python script with given args and return stdout."""
    result = subprocess.run([sys.executable, script_path] + args,
                            capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error running {script_path}: {result.stderr}")
        sys.exit(1)
    return result.stdout.strip()

def main():
    if len(sys.argv) < 2:
        print("Usage: python full_publish.py <video_path> [title_hint]")
        sys.exit(1)
    video_path = sys.argv[1]
    title_hint = sys.argv[2] if len(sys.argv) > 2 else ""
    base_dir = pathlib.Path(__file__).parent.parent  # repo root
    scripts_dir = base_dir / "scripts"

    # 1. Extract thumbnails
    print("🚀 Generating thumbnails via Gemini...")
    # thumbnail_generator.py <video_path> <title_text>
    run_script(str(scripts_dir / "thumbnail_generator.py"), [video_path, title_hint or pathlib.Path(video_path).stem])

    # 2. Generate SEO metadata
    print("🧠 Generating SEO metadata via Gemini...")
    # youtube_seo.py <video_path> <title_hint>
    run_script(str(scripts_dir / "youtube_seo.py"), [video_path, title_hint or pathlib.Path(video_path).stem])
    
    slug = pathlib.Path(video_path).stem
    seo_file = base_dir / "output" / f"seo_{slug}.json"
    
    try:
        with open(seo_file, "r", encoding="utf-8") as f:
            seo_data = json.load(f)
    except Exception as e:
        print(f"⚠️ Cannot read SEO data from {seo_file}: {e}")
        seo_data = {}
        
    title = seo_data.get("title", title_hint or slug)
    description = seo_data.get("description", "Video tạo bởi FlowKit V13.0 - AI Studio")
    tags = seo_data.get("tags", ["FlowKit", "AI"])

    # 3. Upload to YouTube
    print("📤 Uploading video to YouTube...")
    # tags is a list, convert to comma-separated
    tags_arg = ",".join(tags) if isinstance(tags, list) else str(tags)
    run_script(str(scripts_dir / "youtube_uploader.py"), [video_path, title, description, tags_arg])
    print("✅ Full publish pipeline completed!")

if __name__ == "__main__":
    main()
