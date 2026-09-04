"use client";

import { useState, useEffect } from "react";

interface Tram4Data {
  projects: string[];
  musicFiles: string[];
}

export default function Tram4() {
  const [data, setData] = useState<Tram4Data>({ projects: [], musicFiles: [] });
  const [selectedProj, setSelectedProj] = useState("");
  const [selectedMusic, setSelectedMusic] = useState("");
  const [mixing, setMixing] = useState(false);

  useEffect(() => {
    fetch('/api/tram4')
      .then(res => res.json())
      .then(d => {
        setData(d);
        if (d.projects?.length > 0) setSelectedProj(d.projects[0]);
        if (d.musicFiles?.length > 0) setSelectedMusic(d.musicFiles[0]);
      });
  }, []);

  const handleMix = async () => {
    if (!selectedProj || !selectedMusic) return alert("Vui lòng chọn Dự án và Nhạc nền.");
    setMixing(true);
    try {
      const res = await fetch('/api/tram4', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'mix', project: selectedProj, musicFile: selectedMusic })
      });
      if (res.ok) alert("Mix âm thanh và Logo hoàn tất!");
      else alert("Lỗi khi Mix video.");
    } catch {
      alert("Lỗi kết nối.");
    } finally {
      setMixing(false);
    }
  };

  const handleUpload = async () => {
    if (!selectedProj) return;
    try {
      const res = await fetch('/api/tram4', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'upload', project: selectedProj })
      });
      const d = await res.json();
      alert(d.message || d.error);
    } catch {
      alert("Lỗi kết nối.");
    }
  };

  return (
    <div className="p-10 max-w-7xl mx-auto w-full">
      <header className="mb-12">
        <h1 className="text-4xl font-black mb-4">🎧 Trạm 4: Bàn Mix Hậu Kỳ & Xuất Xưởng</h1>
        <p className="text-slate-400 text-lg">Ghép nhạc nền, đóng dấu bản quyền Logo và tự động upload lên YouTube.</p>
      </header>

      {data.projects.length === 0 ? (
        <div className="glass-panel p-16 rounded-3xl text-center border-dashed border-2 border-slate-700">
          <div className="text-6xl mb-4">🎬</div>
          <h3 className="text-2xl font-bold text-slate-300">Chưa có video nào hoàn thành dựng thô</h3>
        </div>
      ) : (
        <div className="glass-panel p-8 rounded-3xl">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            <div>
              <label className="block text-sm font-semibold text-slate-300 mb-2 uppercase">Chọn Dự Án Cần Mix:</label>
              <select 
                value={selectedProj} 
                onChange={e => setSelectedProj(e.target.value)}
                className="w-full bg-black/20 border border-white/10 rounded-xl px-5 py-4 text-white focus:outline-none focus:border-blue-500"
              >
                {data.projects.map((p, i) => <option key={i} value={p}>{p}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-300 mb-2 uppercase">Chọn Nhạc Nền (BGM):</label>
              <select 
                value={selectedMusic} 
                onChange={e => setSelectedMusic(e.target.value)}
                className="w-full bg-black/20 border border-white/10 rounded-xl px-5 py-4 text-white focus:outline-none focus:border-blue-500"
              >
                {data.musicFiles.map((m, i) => <option key={i} value={m}>{m}</option>)}
              </select>
            </div>
          </div>
          
          <div className="flex gap-4">
            <button 
              onClick={handleMix}
              disabled={mixing}
              className={`flex-1 py-4 rounded-xl font-bold transition-all ${mixing ? 'bg-slate-700 text-slate-400 cursor-not-allowed' : 'btn-primary text-white shadow-[0_0_15px_rgba(59,130,246,0.4)]'}`}
            >
              {mixing ? '⚙️ Đang Mix âm thanh và Đóng Logo...' : '🎛️ Mix Lại Video (Lấy Ngay)'}
            </button>
            <button 
              onClick={handleUpload}
              className="flex-1 bg-red-500 hover:bg-red-600 text-white py-4 rounded-xl font-bold shadow-[0_0_15px_rgba(239,68,68,0.4)] transition-all"
            >
              🚀 Đăng Lên YouTube
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
