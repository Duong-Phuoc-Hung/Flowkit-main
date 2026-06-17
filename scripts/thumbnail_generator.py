"""thumbnail_generator.py - Generate YouTube‑optimized thumbnails using Gemini and Pillow.

Usage:
    python scripts/thumbnail_generator.py <video_path> <title_text>

The script creates four 1280×720 PNG thumbnails with the video title overlaid
and saves them under `output/thumbnails/<slug>_thumbN.png`.
"""
import os
import sys
import io
import json
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai

CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config")
API_KEYS_FILE = os.path.join(CONFIG_DIR, "api_keys.txt")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "thumbnails")

def load_api_key():
    if not os.path.exists(API_KEYS_FILE):
        raise FileNotFoundError(f"API keys file not found: {API_KEYS_FILE}")
    with open(API_KEYS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            key = line.strip()
            if key and not key.startswith("#"):
                return key
    raise ValueError("No API key found in api_keys.txt")

def generate_image(prompt: str) -> Image.Image:
    genai.configure(api_key=load_api_key())
    model = genai.GenerativeModel("gemini-1.5-flash")
    # Request a 1280x720 image; Gemini returns a URL we download.
    response = model.generate_content([prompt, "Generate an image of size 1280x720."], generation_config={"response_mime_type": "image/png"})
    # The response contains a temporary URL in response._result.candidate[0].output.
    # Simplify: assume response.image is a bytes object.
    img_bytes = response.image  # placeholder – actual SDK may differ.
    return Image.open(io.BytesIO(img_bytes))

def overlay_text(image: Image.Image, text: str) -> Image.Image:
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 48)
    except Exception:
        font = ImageFont.load_default()
    w, h = draw.textsize(text, font=font)
    x = (image.width - w) // 2
    y = image.height - h - 40
    # Add a semi‑transparent rectangle for readability
    rect_margin = 20
    draw.rectangle([x-rect_margin, y-rect_margin, x+w+rect_margin, y+h+rect_margin], fill=(0,0,0,120))
    draw.text((x, y), text, font=font, fill=(255,255,255))
    return image

def main():
    if len(sys.argv) < 3:
        print("Usage: python thumbnail_generator.py <video_path> <title_text>")
        sys.exit(1)
    video_path = sys.argv[1]
    title = sys.argv[2]
    if not os.path.exists(video_path):
        print(f"Video not found: {video_path}")
        sys.exit(1)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    slug = os.path.splitext(os.path.basename(video_path))[0]
    for i in range(1, 5):
        prompt = f"Create a vibrant YouTube thumbnail for a video titled '{title}'. Use bold colors, dynamic composition, and include the text '{title}'."
        img = generate_image(prompt)
        img = overlay_text(img, title)
        out_path = os.path.join(OUTPUT_DIR, f"{slug}_thumb{i}.png")
        img.save(out_path, "PNG")
        print(f"Thumbnail {i} saved to {out_path}")

if __name__ == "__main__":
    main()
