"use client";
import { useState, useEffect } from "react";

export default function CauHinh() {
  const [nightMode, setNightMode] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/config')
      .then(res => res.json())
      .then(data => {
        setNightMode(data.night_mode || false);
        setLoading(false);
      });
  }, []);

  const handleSave = async () => {
    await fetch('/api/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ night_mode: nightMode })
    });
    alert('Đã lưu cấu hình!');
  };

  return (
    <div className="p-10 max-w-5xl mx-auto w-full">
      <header className="mb-12">
        <h1 className="text-4xl font-black mb-4">⚙️ Cấu Hình Máy (Kloning & Cày Đêm)</h1>
        <p className="text-slate-400 text-lg">Khu vực điều chỉnh thông số lõi, ép khuôn mặt và trích xuất giọng nói độc bản.</p>
      </header>

      <div className="glass-panel p-8 rounded-3xl">
        <h3 className="text-2xl font-bold text-white mb-6">🌙 Chế Độ Cày Đêm (Night Scheduler)</h3>
        
        {loading ? (
          <div className="text-slate-400">Đang tải cấu hình...</div>
        ) : (
          <div className="space-y-6">
            <label className="flex items-center space-x-4 cursor-pointer group">
              <div className={`w-8 h-8 rounded border flex items-center justify-center transition-colors ${nightMode ? 'bg-blue-500 border-blue-500' : 'border-white/20 group-hover:border-white/40'}`}>
                {nightMode && <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>}
              </div>
              <input type="checkbox" className="hidden" checked={nightMode} onChange={(e) => setNightMode(e.target.checked)} />
              <span className="text-slate-300 font-medium select-none group-hover:text-white transition-colors text-lg">
                Bật tính năng Cày Đêm (Hệ thống sẽ ngủ đông ban ngày và chỉ làm việc từ 00:00 - 06:00 sáng)
              </span>
            </label>
            
            <button 
              onClick={handleSave}
              className="btn-primary text-white font-bold py-3 px-8 rounded-xl"
            >
              Lưu Cài Đặt
            </button>
          </div>
        )}
      </div>

      <div className="mt-8 glass-panel p-8 rounded-3xl">
        <h3 className="text-2xl font-bold text-white mb-2">👤 Phòng Kloning (Ép Khuôn Mặt Nhân Vật)</h3>
        <p className="text-slate-400 mb-6">Tải lên ảnh Khuôn mặt thật của bạn. Hệ thống sẽ luôn dùng khuôn mặt bạn thay cho mặt ảo!</p>
        <div className="flex gap-4">
          <input type="text" id="c_name" placeholder="Tên Nhân Vật (VD: Sơn Tùng, Hưng...)" className="bg-black/20 border border-white/10 rounded-xl px-5 py-3 text-white focus:border-blue-500 w-1/3" />
          <input type="file" id="kloning_file" accept="image/png, image/jpeg" className="block w-1/3 text-sm text-slate-400 file:mr-4 file:py-3 file:px-4 file:rounded-xl file:border-0 file:bg-blue-500/20 file:text-blue-400" />
          <button onClick={async () => {
            const name = (document.getElementById('c_name') as HTMLInputElement).value;
            const file = (document.getElementById('kloning_file') as HTMLInputElement).files?.[0];
            if (!name || !file) return alert('Thiếu tên hoặc file!');
            const fd = new FormData(); fd.append('type', 'kloning'); fd.append('c_name', name); fd.append('file', file);
            const r = await fetch('/api/upload-config', { method: 'POST', body: fd });
            const d = await r.json(); alert(d.message || d.error);
          }} className="btn-primary text-white font-bold py-3 px-6 rounded-xl">Lưu Khuôn Mặt</button>
        </div>
      </div>

      <div className="mt-8 glass-panel p-8 rounded-3xl">
        <h3 className="text-2xl font-bold text-white mb-2">🛡️ Đóng Dấu Bản Quyền (Watermark)</h3>
        <p className="text-slate-400 mb-6">Tải Logo kênh của bạn lên. Máy tự động dán góc phải video để chống trộm.</p>
        <div className="flex gap-4 items-center">
          <input type="file" id="logo_file" accept="image/png" className="block w-1/2 text-sm text-slate-400 file:mr-4 file:py-3 file:px-4 file:rounded-xl file:border-0 file:bg-blue-500/20 file:text-blue-400" />
          <button onClick={async () => {
            const file = (document.getElementById('logo_file') as HTMLInputElement).files?.[0];
            if (!file) return alert('Thiếu file!');
            const fd = new FormData(); fd.append('type', 'logo'); fd.append('file', file);
            const r = await fetch('/api/upload-config', { method: 'POST', body: fd });
            const d = await r.json(); alert(d.message || d.error);
          }} className="bg-slate-700 hover:bg-slate-600 text-white font-bold py-3 px-6 rounded-xl transition-all">Lưu Logo</button>
        </div>
      </div>

      <div className="mt-8 glass-panel p-8 rounded-3xl">
        <h3 className="text-2xl font-bold text-white mb-2">🎙️ Kloning Giọng Nói (AI Voice)</h3>
        <p className="text-slate-400 mb-6">Tải 10s đoạn ghi âm giọng thật của bạn. Mọi video sẽ mang giọng của bạn.</p>
        <div className="flex gap-4 items-center">
          <input type="file" id="voice_file" accept="audio/mpeg, audio/wav" className="block w-1/2 text-sm text-slate-400 file:mr-4 file:py-3 file:px-4 file:rounded-xl file:border-0 file:bg-blue-500/20 file:text-blue-400" />
          <button onClick={async () => {
            const file = (document.getElementById('voice_file') as HTMLInputElement).files?.[0];
            if (!file) return alert('Thiếu file!');
            const fd = new FormData(); fd.append('type', 'voice'); fd.append('file', file);
            const r = await fetch('/api/upload-config', { method: 'POST', body: fd });
            const d = await r.json(); alert(d.message || d.error);
          }} className="bg-slate-700 hover:bg-slate-600 text-white font-bold py-3 px-6 rounded-xl transition-all">Trích Xuất Giọng</button>
        </div>
      </div>
    </div>
  );
}
