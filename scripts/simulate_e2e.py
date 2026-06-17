import os
import json
import time
import sys
try: sys.stdout.reconfigure(encoding='utf-8')
except: pass

def simulate_pipeline(error_type=None):
    print("=== BẮT ĐẦU MÔ PHỎNG END-TO-END (GIẢ LẬP) ===")
    
    # 1. Nạp kịch bản
    print("\n[1/6] Nạp kịch bản thô...")
    idea = "Một con rồng bay lượn và chiến đấu với siêu nhân."
    print(f"Kịch bản gốc: {idea}")
    time.sleep(1)
    
    # 2. Sinh JSON
    print("\n[2/6] AI Phân Tích & Sinh JSON (Đã Tối Ưu 1 Đặc Vụ)...")
    time.sleep(1)
    
    # 3. Khởi tạo Project
    print("\n[3/6] Đẩy Project lên Máy chủ Google (Mock API)...")
    project_id = "proj_mock_123"
    print(f"Tạo thành công Project ID: {project_id}")
    time.sleep(1)
    
    if error_type == "400":
        print("\n[4/6] Render Ảnh (Mô phỏng bắt lỗi API_400 nặng nhất)...")
        print("⏳ Waiting – 1 pending, 0 processing…")
        print("❌ Lỗi khi vẽ ảnh tĩnh (Batch API failed liên tục 3 lần)")
        print("🛠️ Kích hoạt giao thức Dọn Rác...")
        print(f"🗑️ Đã xóa sạch 'Vỏ rỗng' trên máy chủ: DELETE /api/projects/{project_id}")
        print("📦 Đã di chuyển kịch bản hỏng vào thư mục '99_bao_loi' để chống lặp vô hạn spam request.")
        print("\n=== KẾT THÚC MÔ PHỎNG (HỆ THỐNG ĐÃ AN TOÀN TRƯỚC LỖI 400) ===")
        return
        
    if error_type == "retry":
        print("\n[4/6] Render Ảnh (Mô phỏng 1 ảnh bị từ chối do Unsafe Prompt)...")
        print("⚠️ Batch completed but some requests failed (1/10 lỗi).")
        print("🔄 [Cứu Hộ Token] Phát hiện 1 ảnh bị lỗi. Đang gửi lệnh REGENERATE_IMAGE chỉ cho cảnh đó (lần 1/3)...")
        time.sleep(1)
        print("✅ [Cứu Hộ Token] Cảnh báo lỗi đã được vẽ lại thành công! Bảo toàn Token của 9 cảnh kia.")
        
    # 4. Render Ảnh
    print("\n[4/6] Render Ảnh & Báo cáo tiến độ (Mock Batch Poll)...")
    print("✅ All GENERATE_IMAGE requests succeeded.")
    time.sleep(1)
    
    # 5. Render Video
    print("\n[5/6] Render Video & Nối File (Mock FFmpeg)...")
    print("✅ All GENERATE_VIDEO requests succeeded.")
    
    if error_type == "network":
        print("\n[!] Báo động rớt mạng khi đang tải video 4K...")
        print("❌ Lỗi tải video: Connection aborted.")
        print("🧹 [Resilient Downloader] Đã quét và xóa file tải dở dang '4k/scene_001.mp4' để tránh làm hỏng FFmpeg ở lần chạy sau.")
        print("\n=== KẾT THÚC MÔ PHỎNG (HỆ THỐNG ĐÃ AN TOÀN TRƯỚC LỖI MẠNG) ===")
        return
        
    import subprocess
    print("Đang gọi FFmpeg để xuất MP4 thật (Cảnh báo: màn hình màu đỏ 3s)...")
    os.makedirs("output", exist_ok=True)
    subprocess.run("ffmpeg -y -f lavfi -i color=c=red:s=1920x1080:d=3 -c:v libx264 -t 3 output/final_mock.mp4", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists("output/final_mock.mp4"):
        print("✅ Đã nối xong video thật: output/final_mock.mp4")
    time.sleep(1)
    
    # 6. Kiểm duyệt & SEO
    print("\n[6/8] Mắt Thần KCS AI Vision...")
    print("[KCS AI] PASS: Video đạt tiêu chuẩn 4K HDR. Cho phép xuất xưởng.")
    
    print("\n[7/8] Sinh SEO Metadata...")
    print("✂️ [SEO Trimmer] Đã cắt tỉa thẻ Tags dài quá 450 ký tự.")
    
    if error_type == "quota":
        print("\n[8/8] Tự Động Xuất Bản YouTube...")
        print("❌ Lỗi YouTube Upload: quotaExceeded")
        print("📦 [Kho Chờ Đăng] Đã đóng gói video và kịch bản vào thư mục '7_cho_upload'. Ngày mai máy sẽ tự đăng tiếp.")
        print("\n=== KẾT THÚC MÔ PHỎNG (HỆ THỐNG ĐÃ BẢO VỆ VIDEO TRƯỚC LỖI QUOTA YOUTUBE) ===")
        return

    print("\n[8/8] Tự Động Xuất Bản YouTube...")
    print("[Auto-Publish] Kích hoạt Upload cho output/final_mock.mp4")
    print("✅ Đã Upload thành công! URL: https://youtube.com/watch?v=mock_abc123")
    
    print("\n=== KẾT THÚC MÔ PHỎNG: HỆ THỐNG HOẠT ĐỘNG HOÀN HẢO TỪ A-Z ===")

if __name__ == "__main__":
    error_type = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "--error-400": error_type = "400"
        elif sys.argv[1] == "--error-retry": error_type = "retry"
        elif sys.argv[1] == "--error-network": error_type = "network"
        elif sys.argv[1] == "--error-quota": error_type = "quota"
        elif sys.argv[1] == "--error": error_type = "400"
        
    simulate_pipeline(error_type)
