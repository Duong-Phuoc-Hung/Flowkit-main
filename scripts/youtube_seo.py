"""youtube_seo.py - Generate SEO metadata for a YouTube video using Gemini.

Usage:
    python scripts/youtube_seo.py <video_path> <title_hint>

The script reads the video file (or its path), extracts basic metadata if needed, then calls the Gemini model
to generate a SEO‑optimized title, description and a list of tags.

Output is written to `output/seo_<slug>.json`.
"""
import os
import sys
import json
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Gemini import – assumes api_keys.txt contains a valid key
import google.generativeai as genai

CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config")
API_KEYS_FILE = os.path.join(CONFIG_DIR, "api_keys.txt")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")

def load_api_key():
    if not os.path.exists(API_KEYS_FILE):
        raise FileNotFoundError("API key file not found: {}".format(API_KEYS_FILE))
    with open(API_KEYS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            key = line.strip()
            if key and not key.startswith("#"):
                return key
    raise ValueError("No API key found in {}".format(API_KEYS_FILE))

def generate_seo(video_path: str, hint: str) -> dict:
    genai.configure(api_key=load_api_key())
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"""You are an expert YouTube SEO specialist.
Given a video about "{hint}" (the video file is at {video_path}), generate:
1. A catchy, SEO-optimized title (max 60 characters).
2. A description (max 500 characters) that includes relevant keywords.
3. A list of 10-12 tags (comma-separated strings) that help the video rank.
Return the result as a pure JSON object with exactly these keys: title (string), description (string), tags (list of strings)."""
    
    response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
    try:
        result = json.loads(response.text)
        tags = result.get("tags", [])
        # BỘ KÉO CẮT TỈA TAGS: Chống lỗi 400 InvalidTags của YouTube (Giới hạn 500 ký tự)
        trimmed_tags = []
        current_len = 0
        for t in tags:
            tag_cost = len(t) + (2 if ' ' in t else 0) + 1 # Tính cả khoảng trắng và dấu phẩy
            if current_len + tag_cost <= 450: # Chừa 50 ký tự an toàn
                trimmed_tags.append(t)
                current_len += tag_cost
        result["tags"] = trimmed_tags
    except Exception as e:
        raise ValueError(f"Unable to parse Gemini response for SEO: {e}")
    return result

def main():
    if len(sys.argv) < 3:
        print("Usage: python youtube_seo.py <video_path> <title_hint>")
        sys.exit(1)
    video_path = sys.argv[1]
    hint = sys.argv[2]
    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        sys.exit(1)
    seo = generate_seo(video_path, hint)
    slug = os.path.splitext(os.path.basename(video_path))[0]
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"seo_{slug}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(seo, f, ensure_ascii=False, indent=2)
    print(f"SEO metadata written to {out_path}")

if __name__ == "__main__":
    main()
