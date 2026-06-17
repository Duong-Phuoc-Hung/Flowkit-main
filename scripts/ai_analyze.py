import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import sys
import os
import json
import google.generativeai as genai
from PIL import Image
from PIL import Image

def main():
    if len(sys.argv) < 2:
        print("Usage: python ai_analyze.py <image_path>")
        sys.exit(1)
        
    img_path = sys.argv[1]
    if not os.path.exists(img_path):
        print(f"Error: Image {img_path} not found")
        sys.exit(1)
        
    config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
    api_keys_file = os.path.join(config_dir, "api_keys.txt")
    learning_file = os.path.join(config_dir, "learning.json")
    
    api_keys = []
    try:
        with open(api_keys_file, "r", encoding="utf-8") as f:
            for line in f:
                key = line.strip()
                if key and not key.startswith("#"): api_keys.append(key)
    except:
        pass
        
    if not api_keys:
        print("Error: No API key found in config/api_keys.txt")
        sys.exit(1)
        
    genai.configure(api_key=api_keys[0])
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    try:
        img = Image.open(img_path)
        prompt = "Bạn là Chuyên gia phân tích dữ liệu YouTube Tối Cao. Dựa vào bức ảnh thống kê này, hãy chỉ ra điểm mạnh/điểm yếu của video, và viết ra TÓM TẮT 3 QUY LUẬT (Rules) ĐẮT GIÁ NHẤT bằng tiếng Việt để Đạo diễn AI áp dụng cho kịch bản tiếp theo nhằm tăng Lượt View. Chỉ trả về 3 dòng quy luật rõ ràng, không nói dài dòng."
        response = model.generate_content([prompt, img])
        
        rules = response.text
        with open(learning_file, "w", encoding="utf-8") as f: 
            json.dump({"rules": rules}, f, ensure_ascii=False)
            
        print("SUCCESS")
        print(rules)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
