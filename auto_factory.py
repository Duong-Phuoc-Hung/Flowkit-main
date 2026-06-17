import requests
import time
import os
import json
import subprocess
import shutil
import flowkit.api_client as api
from datetime import datetime
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import traceback
import google.generativeai as genai
import concurrent.futures
import sys
import os

# Fix print unicode error on windows
sys.stdout.reconfigure(encoding='utf-8')

# Add scripts dir to path to import batch_poll
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "scripts")))
from batch_poll import poll_batch
# CẤU HÌNH HỆ THỐNG PIPELINE V6.0 (MASTERPIECE)
# ==========================================
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

for d in [CONFIG_DIR, MUSIC_DIR, DIR_1, DIR_2, DIR_3, DIR_3_5, DIR_3_8, DIR_4, EXPORTS_DIR]:
    os.makedirs(d, exist_ok=True)

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception:
        print("\n[BÁO ĐỘNG ĐỎ] KHÔNG TÌM THẤY FFMPEG!")
        print("Hệ thống không thể nối video nếu thiếu FFmpeg. Vui lòng cài đặt và đưa vào PATH.")
        sys.exit(1)

check_ffmpeg()

if not os.path.exists(API_KEYS_FILE):
    with open(API_KEYS_FILE, "w", encoding="utf-8") as f:
        f.write("YOUR_GEMINI_API_KEY_HERE\n")

if not os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f: json.dump({"night_mode": False}, f)
        
if not os.path.exists(CHARACTERS_FILE):
    with open(CHARACTERS_FILE, "w", encoding="utf-8") as f: json.dump({}, f)

API_KEYS = []
with open(API_KEYS_FILE, "r", encoding="utf-8") as f:
    for line in f:
        key = line.strip()
        if key and not key.startswith("#"): API_KEYS.append(key)

current_key_idx = 0
def config_gemini():
    if API_KEYS: genai.configure(api_key=API_KEYS[current_key_idx])

config_gemini()
API_URL = "http://127.0.0.1:8100/api"
DEFAULT_ORIENTATION = "HORIZONTAL"

def update_status(progress, phase, log_msg):
    print(f"[{progress}%] {phase}: {log_msg}")
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump({"progress": progress, "phase": phase, "log": log_msg}, f, ensure_ascii=False)
    except Exception as e: print(f\'Warning: {e}\')

def is_night_mode_active():
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            if json.load(f).get("night_mode"):
                return not (0 <= datetime.now().hour <= 6)
    except Exception as e: print(f\'Warning: {e}\')
    return False

def check_stuck_projects():
    stuck_3 = [f for f in os.listdir(DIR_3) if f.endswith(".json")]
    stuck_3_8 = [f for f in os.listdir(DIR_3_8) if f.endswith(".json")]
    total_stuck = len(stuck_3) + len(stuck_3_8)
    if total_stuck > 0:
        update_status(0, "🛠️ Bác Sĩ Phục Hồi", f"Phát hiện {total_stuck} dự án bị kẹt do rớt mạng/cúp điện hôm trước. Đang khôi phục...")
        time.sleep(3)

def expand_idea_to_json(idea_text):
    global current_key_idx
    if not API_KEYS: return None
    
    fact_check_mode = False
    if idea_text.startswith("[FACT_CHECK_MODE]\n"):
        fact_check_mode = True
        idea_text = idea_text.replace("[FACT_CHECK_MODE]\n", "")

    try:
        with open(os.path.join(CONFIG_DIR, "learning.json"), "r", encoding="utf-8") as f:
            ai_rules = json.load(f).get("rules", "")
    except: ai_rules = ""

    base_prompt = f"""Bạn là Đạo diễn AI xuất sắc nhất Hollywood. Kịch bản GỐC: "{idea_text}"
Nhiệm vụ: Trả về JSON thuần (story, mood, characters, scenes). Mood: action, sad, epic, chill, happy.
Cấu trúc scenes: prompt (Mô tả cảnh tĩnh), video_prompt (GÓC MÁY ĐỘNG), narrator_text (dưới 15 từ), voice_gender (Nam/Nữ), character_names.
CHÚ Ý GÓC MÁY (video_prompt): BẮT BUỘC phải dùng các thuật ngữ điện ảnh (VD: Drone flythrough, extreme close up, slow motion pan, tracking shot, FPV, cinematic lighting) để video giống phim bom tấn.

QUY TRÌNH TƯ DUY NỘI TẠI (Chain of Thought): 
Hãy tự phân tích điểm yếu của cốt truyện gốc, tự đẩy cao trào lên mức tối đa, sửa chữa các lỗ hổng logic. Sau đó TRẢ VỀ DUY NHẤT 1 CHUỖI JSON CHUẨN XÁC, không có bất kỳ văn bản nào khác.

QUY LUẬT TÒA SOẠN (BẮT BUỘC TUÂN THỦ TỪ DỮ LIỆU HỌC MÁY):
{ai_rules}"""

    if fact_check_mode:
        base_prompt += "\nLƯU Ý QUAN TRỌNG (CHẾ ĐỘ KHẢO CỔ): Đây là video Tôn trọng Sự Thật. Bạn BẮT BUỘC phải đối chiếu mốc thời gian, nhân vật, số liệu thực tế trước khi viết kịch bản. TUYỆT ĐỐI KHÔNG BỊA ĐẶT."

    for attempt in range(5):
        try:
            update_status(3, "AI Sáng Tác", "Đang nén 3 Đặc vụ thành 1 để phân tích và viết kịch bản JSON siêu tốc (Tiết kiệm Token)...")
            res_final = genai.GenerativeModel('gemini-2.5-flash').generate_content(base_prompt, generation_config={"response_mime_type": "application/json"})
            
            final_json = json.loads(res_final.text)
            
            # SMART SCENE SPLITTING (Chống Lỗi Âm Thanh Đơ Video)
            new_scenes = []
            for scene in final_json.get("scenes", []):
                nt = scene.get("narrator_text", "")
                words = nt.split()
                if len(words) > 22: # Nếu dài hơn 8 giây đọc
                    mid = len(words) // 2
                    scene1 = scene.copy()
                    scene1["narrator_text"] = " ".join(words[:mid])
                    scene2 = scene.copy()
                    scene2["narrator_text"] = " ".join(words[mid:])
                    scene2["prompt"] = scene2.get("prompt", "") + " (Tiếp nối)"
                    new_scenes.extend([scene1, scene2])
                else:
                    new_scenes.append(scene)
            final_json["scenes"] = new_scenes
            
            return final_json
        except Exception as e:
            if len(API_KEYS) > 1:
                current_key_idx = (current_key_idx + 1) % len(API_KEYS)
                update_status(5, "Lỗi Quota", f"🔄 Đổi sang Key số {current_key_idx + 1}")
                config_gemini()
            else: time.sleep(30)
    return None

def create_subtitle_file(srt_path, text):
    with open(srt_path, "w", encoding="utf-8") as f: f.write(f"1\n00:00:00,000 --> 00:00:08,000\n{text}\n")

def generate_suno_music(mood):
    try:
        update_status(92, "🎼 Sáng Tác Nhạc Độc Bản", "Suno AI đang soạn một bản nhạc hoàn toàn mới...")
        res = requests.post(f"{API_URL}/music/generate", json={
            "prompt": f"an epic instrumental track for {mood} movie, cinematic, no vocals",
            "instrumental": True, "custom_mode": False, "poll": True
        })
        if res.status_code == 200:
            task_id = res.json().get('task_id')
            if task_id:
                dl_res = requests.post(f"{API_URL}/music/tasks/{task_id}/download").json()
                dl = dl_res.get('downloaded', [])
                if dl: return dl[0]['path']
    except Exception as e: print(f\'Warning: {e}\')
    return None

def process_input_stories():
    if is_night_mode_active(): return
    files = [f for f in os.listdir(DIR_1) if f.lower().endswith(".txt")]
    for filename in files:
        slug = filename.replace(".txt", "")
        update_status(5, "Đang Dịch Kịch Bản", f"Đang xử lý {filename}...")
        with open(os.path.join(DIR_1, filename), "r", encoding="utf-8") as f: idea = f.read()
        script_data = expand_idea_to_json(idea)
        if script_data:
            with open(os.path.join(DIR_2, f"{slug}.json"), "w", encoding="utf-8") as f: json.dump(script_data, f, ensure_ascii=False, indent=2)
            try:
                os.remove(os.path.join(DIR_1, filename))
            except OSError:
                pass
            update_status(10, "Kịch Bản Đã Sẵn Sàng", f"Kịch bản {slug} chờ bạn duyệt!")

def process_render_images():
    if is_night_mode_active(): return
    files = [f for f in os.listdir(DIR_3) if f.lower().endswith(".json")]
    for filename in files:
        slug = filename.replace(".json", "")
        path = os.path.join(DIR_3, filename)
        try:
            with open(path, "r", encoding="utf-8") as f: script_data = json.load(f)
            update_status(15, "Đang Khởi Tạo Project", f"Đẩy {slug} lên máy chủ...")
            p_id = api.post(f"{API_URL}/projects", json={"name": slug, "story": script_data.get("story", ""), "material": "3d_pixar", "characters": script_data.get("characters", [])}).json().get('id')
            if not p_id: continue
            
            try: # KLONING NHÂN VẬT
                with open(CHARACTERS_FILE, "r", encoding="utf-8") as f: cloned_chars = json.load(f)
                chars_in_proj = api.get(f"{API_URL}/projects/{p_id}/characters").json()
                for c in chars_in_proj:
                    c_name = c.get("name", "")
                    if c_name in cloned_chars:
                        update_status(16, "Kloning Nhân Vật", f"Đang ép khuôn mặt cho {c_name}")
                        api.patch(f"{API_URL}/characters/{c['id']}", json={"media_id": cloned_chars[c_name]})
            except Exception as e: print(f\'Warning: {e}\')

            v_id = api.post(f"{API_URL}/videos", json={"project_id": p_id, "title": slug, "display_order": 0}).json().get('id')
            created_scenes = []
            for i, scene in enumerate(script_data.get("scenes", [])):
                payload = {"video_id": v_id, "display_order": i, "prompt": scene.get("prompt", ""), "video_prompt": scene.get("video_prompt", ""), "narrator_text": scene.get("narrator_text", ""), "character_names": scene.get("character_names", []), "chain_type": "ROOT" if i == 0 else "CONTINUATION"}
                if created_scenes: payload["parent_scene_id"] = created_scenes[-1]['id']
                s_res = requests.post(f"{API_URL}/scenes", json=payload)
                if s_res.status_code == 200:
                    s_obj = s_res.json()
                    s_obj['voice_gender'], s_obj['narrator_text'] = scene.get('voice_gender', 'Nữ'), scene.get('narrator_text', '')
                    created_scenes.append(s_obj)

            char_reqs = [{"type": "GENERATE_CHARACTER_IMAGE", "project_id": p_id, "character_id": c['id'], "video_id": v_id} for c in api.get(f"{API_URL}/projects/{p_id}/characters").json() if not c.get('media_id')]
            if char_reqs:
                api.post(f"{API_URL}/requests/batch", json={"requests": char_reqs})
                update_status(20, "Tạo Ảnh Nhân Vật", "Đang xử lý khuôn mặt...")
                success = poll_batch(p_id, "GENERATE_CHARACTER_IMAGE", max_retries=2)
                if not success:
                    raise Exception("Lỗi khi vẽ ảnh nhân vật (Batch API failed)")

            update_status(30, "Đang Vẽ Ảnh Tĩnh", "Bắt đầu vẽ ảnh AI...")
            api.post(f"{API_URL}/requests/batch", json={"requests": [{"type": "GENERATE_IMAGE", "video_id": v_id, "scene_id": s['id'], "project_id": p_id, "orientation": DEFAULT_ORIENTATION} for s in created_scenes]})
            
            # CƠ CHẾ SMART RETRY (CỨU HỘ TOKEN) CHO ẢNH
            for attempt in range(3):
                success = poll_batch(v_id, "GENERATE_IMAGE", max_retries=2)
                if success: break
                
                final_scenes = requests.get(f"{API_URL}/scenes?video_id={v_id}").json()
                failed_scenes = [s for s in final_scenes if s.get(f"{DEFAULT_ORIENTATION.lower()}_image_status") == "FAILED"]
                if not failed_scenes: break # Lỗi mạng hoặc Timeout
                
                update_status(35, "Tự Động Cứu Hộ", f"Phát hiện {len(failed_scenes)} ảnh bị lỗi do Google từ chối. Đang vẽ lại để cứu Token...")
                api.post(f"{API_URL}/requests/batch", json={"requests": [{"type": "REGENERATE_IMAGE", "video_id": v_id, "scene_id": s['id'], "project_id": p_id, "orientation": DEFAULT_ORIENTATION} for s in failed_scenes]})
                
            if not success:
                raise Exception("Lỗi khi vẽ ảnh tĩnh (Đã tự động cứu hộ 3 lần nhưng không thành công)")

            update_status(43, "Tạo Ảnh Hoàn Tất", "Toàn bộ ảnh tĩnh đã vẽ xong, tự động chuyển sang Dựng Video!")

            
            script_data.update({'project_id': p_id, 'video_id': v_id, 'created_scenes': created_scenes})
            with open(path, "w", encoding="utf-8") as f: json.dump(script_data, f, ensure_ascii=False, indent=2)
            shutil.move(path, os.path.join(DIR_3_8, filename)) # XẢ THẲNG VÀO TRẠM DỰNG VIDEO
            # update_status(45, "Chờ Duyệt Ảnh", f"Dự án {slug} vẽ xong ảnh. Hãy sang Trạm 2.5 để duyệt (Chống lỗi)!")

        except Exception as e:
            traceback.print_exc()
            update_status(0, "LỖI", str(e))
            
            # XÓA VỎ RỖNG: Dọn sạch rác trên Database nếu có lỗi xảy ra
            if 'p_id' in locals() and p_id:
                try: requests.delete(f"{API_URL}/projects/{p_id}")
                except Exception as e: print(f\'Warning: {e}\')
                
            # CHỐNG LẶP VÔ HẠN: Di chuyển file bị lỗi ra thư mục khác
            err_dir = os.path.abspath("99_bao_loi")
            os.makedirs(err_dir, exist_ok=True)
            try: shutil.move(path, os.path.join(err_dir, filename))
            except Exception as e: print(f\'Warning: {e}\')

def process_render_video():
    if is_night_mode_active(): return
    files = [f for f in os.listdir(DIR_3_8) if f.lower().endswith(".json")]
    for filename in files:
        slug = filename.replace(".json", "")
        path = os.path.join(DIR_3_8, filename)
        try:
            with open(path, "r", encoding="utf-8") as f: script_data = json.load(f)
            v_id, p_id, created_scenes = script_data.get('video_id'), script_data.get('project_id'), script_data.get('created_scenes', [])
            
            update_status(45, "Đang Dựng Video", "Bắt đầu chuyển động hóa AI...")
            requests.post(f"{API_URL}/requests/batch", json={"requests": [{"type": "GENERATE_VIDEO", "video_id": v_id, "scene_id": s['id'], "project_id": p_id, "orientation": DEFAULT_ORIENTATION} for s in created_scenes]})
            
            # CƠ CHẾ SMART RETRY (CỨU HỘ TOKEN) CHO VIDEO
            for attempt in range(3):
                success = poll_batch(v_id, "GENERATE_VIDEO", max_retries=2)
                if success: break
                
                final_scenes = requests.get(f"{API_URL}/scenes?video_id={v_id}").json()
                failed_scenes = [s for s in final_scenes if s.get(f"{DEFAULT_ORIENTATION.lower()}_video_status") == "FAILED"]
                if not failed_scenes: break # Lỗi mạng hoặc Timeout
                
                update_status(46, "Cứu Hộ Video", f"Phát hiện {len(failed_scenes)} video bị lỗi. Đang Render lại để cứu Token...")
                api.post(f"{API_URL}/requests/batch", json={"requests": [{"type": "REGENERATE_VIDEO", "video_id": v_id, "scene_id": s['id'], "project_id": p_id, "orientation": DEFAULT_ORIENTATION} for s in failed_scenes]})

            if not success:
                raise Exception("Lỗi khi dựng video động (Đã tự động cứu hộ 3 lần nhưng không thành công)")
            # LÀM MỚI URL TRƯỚC KHI RENDER (Chống lỗi 404 Expired)
            update_status(46, "Làm Mới Dữ Liệu", "Đang gia hạn các đường link tải hình ảnh/video từ Google...")
            try: requests.post(f"{API_URL}/flow/refresh-urls/{p_id}", timeout=15)
            except Exception as e: print(f"Lỗi refresh URL: {e}")

            final_scenes = requests.get(f"{API_URL}/scenes?video_id={v_id}").json()
            if isinstance(final_scenes, dict) and "detail" in final_scenes:
                update_status(0, "MẤT DỮ LIỆU", f"Dự án {slug} không còn tồn tại trên máy chủ API (bị xóa db). Tự động đẩy lại quá trình vẽ ảnh!")
                shutil.move(path, os.path.join(DIR_3, filename))
                continue
                
            for i, s in enumerate(final_scenes):
                s['voice_gender'], s['narrator_text'] = created_scenes[i].get('voice_gender', 'Nữ'), created_scenes[i].get('narrator_text', '')

            download_and_concat_fixed(slug, script_data.get("mood", "action"), final_scenes)
            shutil.move(path, os.path.join(DIR_4, filename))
            update_status(0, "Sẵn Sàng", f"Dự án {slug} đã hoàn tất Đóng Dấu & Phối Nhạc!")
        except Exception as e:
            traceback.print_exc()
            update_status(0, "LỖI", str(e))
            # CHỐNG LẶP VÔ HẠN: Di chuyển file bị lỗi ra thư mục khác
            err_dir = os.path.abspath("99_bao_loi")
            os.makedirs(err_dir, exist_ok=True)
            try: shutil.move(path, os.path.join(err_dir, filename))
            except Exception as e: print(f\'Warning: {e}\')

def process_single_scene(args):
    i, s, total, slug, outdir, voice_clone_file = args
    perc = 60 + int((i/total)*20)
    update_status(perc, f"Đang Mix Thoại ({i+1}/{total})", "Đang dựng thô và lồng phụ đề...")
    
    idx3 = f"{s.get('display_order', i):03d}"
    url = s.get(f'{DEFAULT_ORIENTATION.lower()}_video_url') or s.get(f'{DEFAULT_ORIENTATION.lower()}_upscale_url')
    if not url: return None
        
    canonical = f"{outdir}/4k/scene_{idx3}.mp4"
    if not os.path.exists(canonical):
        try:
            with open(canonical, 'wb') as f:
                for chunk in requests.get(url, stream=True, timeout=30).iter_content(chunk_size=8192): f.write(chunk)
        except Exception as e:
            if os.path.exists(canonical): os.remove(canonical) # Dọn ngay file hỏng nếu rớt mạng
            raise e
            
    nt, vg = s.get('narrator_text', '').strip(), s.get('voice_gender', 'Nữ')
    tts_abs, srt_abs = f"{outdir}/tts/scene_{idx3}.wav", f"{outdir}/tts/scene_{idx3}.srt"
    
    if nt and not os.path.exists(tts_abs): 
        # CƠ CHẾ TTS BACKOFF: Thử lại 3 lần nếu máy chủ từ chối
        for retry in range(3):
            if os.path.exists(voice_clone_file):
                subprocess.run(f'edge-tts --voice "vi-VN-NamMinhNeural" --text "{nt}" --write-media "{tts_abs}"', shell=True)
            else:
                subprocess.run(f'edge-tts --voice {"vi-VN-NamMinhNeural" if "Nam" in vg else "vi-VN-HoaiMyNeural"} --text "{nt}" --write-media "{tts_abs}"', shell=True)
            if os.path.exists(tts_abs): break
            import time
            time.sleep(5)
            
    if nt: create_subtitle_file(srt_abs, nt)
        
    norm_file, vf_base = f"norm/scene_{idx3}.mp4", f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,eq=contrast=1.1:saturation=1.2"
    
    # HIỆU ỨNG ĐIỆN ẢNH (Cinematic Subtitles - Phụ đề Vàng Đậm viền đen chuyên nghiệp)
    vf = f"{vf_base},subtitles='tts/scene_{idx3}.srt':force_style='Fontname=Arial,Fontsize=22,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=2,Alignment=2,MarginV=40'" if nt else vf_base

    # Tối ưu hóa FFMPEG: Tách biến để dễ đọc & Dùng preset ultrafast tăng tốc độ Render
    base_cmd = [
        "ffmpeg", "-y", "-i", f"4k/scene_{idx3}.mp4"
    ]
    
    if os.path.exists(tts_abs):
        base_cmd.extend([
            "-i", f"tts/scene_{idx3}.wav",
            "-filter_complex", "[0:a]volume=0.3[amb];[1:a]volume=1.2[tts];[amb][tts]amix=inputs=2:duration=first[aout]",
            "-map", "0:v", "-map", "[aout]"
        ])
    else:
        base_cmd.extend(["-map", "0:v", "-map", "0:a?"])
        
    base_cmd.extend([
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
        "-vf", vf, "-r", "24", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", norm_file
    ])
    
    try:
        subprocess.run(base_cmd, cwd=outdir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception as e:
        print(f"[LỖI FFMPEG] Cảnh {idx3}: {e}")
    if os.path.exists(f"{outdir}/{norm_file}"): return norm_file
    return None

def download_and_concat_fixed(slug, mood, scenes):
    outdir = os.path.abspath(f"{EXPORTS_DIR}/{slug}")
    os.makedirs(f"{outdir}/4k", exist_ok=True)
    os.makedirs(f"{outdir}/tts", exist_ok=True)
    os.makedirs(f"{outdir}/norm", exist_ok=True)
    
    total = len(scenes)
    voice_clone_file = os.path.abspath(os.path.join(CONFIG_DIR, "voice_clone.wav"))
    
    update_status(60, "Khởi Động Đa Luồng", "Đang nạp 100% công suất FFMPEG xử lý song song...")
    args_list = [(i, s, total, slug, outdir, voice_clone_file) for i, s in enumerate(scenes)]
    
    # XỬ LÝ ĐA LUỒNG TĂNG TỐC GẤP 5 LẦN
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_single_scene, args_list))
    
    concat_list = [r for r in results if r]
    
    with open(f"{outdir}/concat.txt", "w", encoding="utf-8") as f:
        for fpath in concat_list: f.write(f"file '{fpath}'\n")
            
    final_raw = "raw_concat.mp4"
    update_status(90, "Đang Ghép Nối", "Đang nối toàn bộ video...")
    subprocess.run(f'ffmpeg -y -f concat -safe 0 -i concat.txt -c copy "{final_raw}"', shell=True, cwd=outdir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # SUNO AI & WATERMARK
    suno_track = generate_suno_music(mood)
    bgm_path = os.path.abspath(suno_track) if suno_track and os.path.exists(suno_track) else (os.path.abspath(f"{MUSIC_DIR}/{mood}.mp3") if os.path.exists(f"{MUSIC_DIR}/{mood}.mp3") else os.path.abspath(DEFAULT_BGM))
    
    logo_path = os.path.abspath(LOGO_FILE)
    final_out = f"{slug}_HOAN_CHINH.mp4"
    update_status(95, "Phối Âm & Đóng Dấu", "Đang đóng dấu Logo bản quyền và ghép nhạc nền...")
    
    if os.path.exists(logo_path):
        cmd = f'ffmpeg -y -i "{final_raw}" -stream_loop -1 -i "{bgm_path}" -i "{logo_path}" -filter_complex "[2:v]scale=150:-1[logo];[0:v][logo]overlay=main_w-overlay_w-20:20[vout];[0:a]volume=1.0[orig];[1:a]volume=0.25[bgm];[orig][bgm]amix=inputs=2:duration=first[aout]" -map "[vout]" -map "[aout]" -c:v libx264 -preset fast -crf 18 -c:a aac -b:a 192k -shortest "{final_out}"'
    else:
        cmd = f'ffmpeg -y -i "{final_raw}" -stream_loop -1 -i "{bgm_path}" -filter_complex "[0:a]volume=1.0[orig];[1:a]volume=0.25[bgm];[orig][bgm]amix=inputs=2:duration=first[aout]" -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k -shortest "{final_out}"'
        
    subprocess.run(cmd, shell=True, cwd=outdir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # ẢNH BÌA YOUTUBE (THUMBNAIL GENERATOR)
    update_status(98, "Thiết Kế Ảnh Bìa", "Đang dùng Gemini tạo 4 Ảnh bìa YouTube chuyên nghiệp...")
    try:
        thumb_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "scripts", "thumbnail_generator.py"))
        subprocess.run([sys.executable, thumb_script, final_out, slug], cwd=outdir, check=True)
    except Exception as e:
        print(f"Lỗi khi tạo Thumbnail bằng Gemini: {e}")
        # Fallback to basic ffmpeg frame extraction if Gemini fails
        thumb_dir = os.path.join(outdir, "Thumbnails")
        os.makedirs(thumb_dir, exist_ok=True)
        base_frame = os.path.join(thumb_dir, "base_frame.jpg")
        subprocess.run(f'ffmpeg -y -i "{final_out}" -ss 00:00:03 -vframes 1 "{base_frame}"', shell=True, cwd=outdir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # TIKTOK 9:16 AUTO-CROP
    update_status(99, "Ép Khuôn TikTok", "Đang cắt khung hình dọc 9:16 cho nền tảng di động...")
    tiktok_out = f"{slug}_TIKTOK_9x16.mp4"
    cmd_tiktok = f'ffmpeg -y -i "{final_out}" -vf "crop=ih*(9/16):ih,scale=1080:1920" -c:a copy "{tiktok_out}"'
    subprocess.run(cmd_tiktok, shell=True, cwd=outdir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # SMART GARBAGE COLLECTOR (Dọn Rác Tiết Kiệm Ổ Cứng)
    update_status(100, "Dọn Rác Thông Minh", "Đang xóa các file trung gian (4K thô, TTS, Norm) để tiết kiệm ổ cứng...")
    try:
        shutil.rmtree(os.path.join(outdir, "4k"), ignore_errors=True)
        shutil.rmtree(os.path.join(outdir, "tts"), ignore_errors=True)
        shutil.rmtree(os.path.join(outdir, "norm"), ignore_errors=True)
        # if os.path.exists(os.path.join(outdir, "concat.txt")):
        #     os.remove(os.path.join(outdir, "concat.txt"))

        # ----- 4. MẮT THẦN KCS (QC TỰ ĐỘNG BẰNG AI VISION) -----
        update_status(95, "ĐANG KIỂM DUYỆT (KCS)", "Mắt thần AI đang soi lỗi từng khung hình...")
        try:
            final_out_abs = os.path.join(outdir, final_out)
            subprocess.run([sys.executable, "scripts/review_video.py", final_out_abs], check=True)
            qc_msg = "Kiểm duyệt KCS thành công (Không có lỗi nhiễu mờ)"
        except Exception:
            update_status(0, "KCS TỪ CHỐI", "Phát hiện video lỗi. Đang gửi về xưởng để Render lại toàn bộ...")
            script_in_4 = os.path.abspath(f"4_hoan_thanh/{slug}.json")
            if os.path.exists(script_in_4): shutil.move(script_in_4, os.path.abspath(f"3.8_dang_dung_video/{slug}.json"))
            return # Ngưng xuất bản

        # ----- 5. TẠO SEO METADATA BẰNG GEMINI -----
        update_status(97, "Tạo Meta SEO", "Đang phân tích video để tạo tiêu đề và thẻ Tags YouTube...")
        try:
            seo_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "scripts", "youtube_seo.py"))
            subprocess.run([sys.executable, seo_script, final_out, slug], cwd=outdir, check=True)
        except Exception as e:
            print(f"Lỗi khi tạo SEO: {e}")

        # ----- 6. TỰ ĐỘNG XUẤT BẢN YOUTUBE -----
        update_status(100, "Tự Động Xuất Bản", "Đang đẩy Video 4K lên kênh YouTube...")
        try:
            yt_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "scripts", "youtube_uploader.py"))
            # Kích hoạt Upload Thực Tế lên YouTube
            subprocess.run([sys.executable, yt_script, final_out_abs, "upload"], check=True)
            print(f"[Auto-Publish] Upload thành công: {final_out_abs}")
        except subprocess.CalledProcessError as e:
            if e.returncode == 2:
                print(f"[BÁO ĐỘNG] Hết Quota YouTube! Đang chuyển video sang kho 7_cho_upload...")
                wait_dir = os.path.abspath("7_cho_upload")
                os.makedirs(wait_dir, exist_ok=True)
                try: shutil.move(outdir, os.path.join(wait_dir, slug))
                except Exception as e: print(f\'Warning: {e}\')
                update_status(0, "KHO CHỜ ĐĂNG", f"Dự án {slug} đã đưa vào kho chờ vì hết Quota YouTube.")
                return
            else:
                print(f"Lỗi YouTube Upload (Mã lỗi {e.returncode}): {e}")
        except Exception as e:
            print(f"Lỗi YouTube Upload: {e}")

    except Exception as e:
        print(f"Lỗi khi ghép video cho {slug}: {e}")
        return

    update_status(100, "XUẤT BẢN THÀNH CÔNG", f"Dự án {slug} đã hoàn thiện 100%! {qc_msg}")

def run_factory():
    update_status(0, "Khởi Động Máy", "Đang quét các file rác và lỗi cũ...")
    check_stuck_projects()
    if is_night_mode_active(): update_status(0, "Cày Đêm Bật", "Máy đang ngủ đông chờ 00:00...")
    else: update_status(0, "Sẵn Sàng", "Hệ thống đang hoạt động trơn tru...")
        
    while True:
        # Check Extension Health first
        try:
            health = requests.get(f"{API_URL.replace('/api', '/health')}", timeout=5).json()
            if not health.get("extension_connected"):
                update_status(0, "Mất Kết Nối", "Vui lòng mở Google Chrome và bật Extension FlowKit!")
                time.sleep(10)
                continue
        except Exception:
            update_status(0, "Mất Kết Nối", "Đang đợi máy chủ Backend khởi động...")
            time.sleep(10)
            continue
            
        process_input_stories()
        process_render_images()
        process_render_video()
        time.sleep(5)

if __name__ == "__main__":
    run_factory()