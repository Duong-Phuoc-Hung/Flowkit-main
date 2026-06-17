import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import sys
import os
import json
import yt_dlp
import uuid
import google.generativeai as genai

def main():
    if len(sys.argv) < 3:
        print("Usage: python spy_clone.py <url> <topic>")
        sys.exit(1)
        
    url = sys.argv[1]
    topic = sys.argv[2]
    
    config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
    api_keys_file = os.path.join(config_dir, "api_keys.txt")
    learning_file = os.path.join(config_dir, "learning.json")
    dir_1 = os.path.join(os.path.dirname(os.path.dirname(__file__)), '1_nhap_lieu')
    
    api_keys = []
    try:
        with open(api_keys_file, "r", encoding="utf-8") as f:
            for line in f:
                key = line.strip()
                if key and not key.startswith("#"): api_keys.append(key)
    except:
        pass
        
    if not api_keys:
        print("Error: No API key found")
        sys.exit(1)
        
    import tempfile
    temp_dir = tempfile.gettempdir()
    temp_name = f"spy_{uuid.uuid4().hex[:8]}"
    temp_path = os.path.join(temp_dir, temp_name)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': temp_path + '.%(ext)s',
        'download_ranges': lambda info, ydl: [{'start_time': 0, 'end_time': 180}],
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192',}],
        'quiet': True,
        'no_warnings': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        audio_path = temp_path + ".mp3"
        genai.configure(api_key=api_keys[0])
        uploaded_file = genai.upload_file(path=audio_path)
        
        prompt = f"""Bạn là Điệp viên Phân tích Kênh YouTube. Nhiệm vụ của bạn:
1. Hãy lắng nghe file âm thanh này (đây là video của kênh đối thủ).
2. Hãy bóc tách 3 QUY LUẬT LÀM VIDEO của họ (Ví dụ: Câu hook họ giật tít thế nào, nhịp độ nói nhanh hay chậm, họ dùng yếu tố bất ngờ ra sao).
3. Đóng vai Tòa Soạn V10.0, hãy dựa CHÍNH XÁC vào 3 quy luật đó để VIẾT MỘT Ý TƯỞNG KỊCH BẢN MỚI về chủ đề: "{topic}".

Trả về dưới định dạng:
LUAT_MOI: [Liệt kê 3 quy luật]
Y_TUONG_MOI: [Viết 1 đoạn ý tưởng kịch bản]"""

        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content([prompt, uploaded_file])
        
        text = response.text
        try:
            luat_moi = text.split("Y_TUONG_MOI:")[0].replace("LUAT_MOI:", "").strip()
            y_tuong_moi = text.split("Y_TUONG_MOI:")[1].strip()
            
            with open(learning_file, "w", encoding="utf-8") as f: 
                json.dump({"rules": luat_moi}, f, ensure_ascii=False)
                
            proj_name = "Clone_" + str(uuid.uuid4())[:8]
            if not os.path.exists(dir_1): os.makedirs(dir_1)
            with open(os.path.join(dir_1, f"{proj_name}.txt"), "w", encoding="utf-8") as f:
                f.write(y_tuong_moi)
                
            genai.delete_file(uploaded_file.name)
            if os.path.exists(audio_path): os.remove(audio_path)
            
            print("SUCCESS")
            print(f"Project: {proj_name}")
            print(f"Rules: {luat_moi}")
        except Exception as e:
            print(f"Error parsing Gemini response: {e}\nRaw Response:\n{text}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
