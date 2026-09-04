"use client";

import { useState, useEffect } from "react";

export default function Home() {
  const [idea, setIdea] = useState("");
  const [projName, setProjName] = useState("");
  const [factCheck, setFactCheck] = useState(false);
  const [status, setStatus] = useState<"idle" | "loading" | "success">("idle");

  const handleSubmit = async () => {
    if (!projName || !idea) return;
    setStatus("loading");
    
    try {
      const res = await fetch('/api/submit-idea', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ projName, idea, factCheck })
      });
      
      if (res.ok) {
        setStatus("success");
        setTimeout(() => {
          setProjName("");
          setIdea("");
          setStatus("idle");
        }, 3000);
      } else {
        setStatus("idle");
        alert("Lỗi khi gửi kịch bản.");
      }
    } catch (e) {
      setStatus("idle");
      alert("Lỗi kết nối tới Server.");
    }
  };

  const handleNameChange = (val: string) => {
    const slug = val
      .replace(/Đ/g, "D")   // uppercase Đ trước khi toLowerCase
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "") // Xóa dấu tiếng Việt
      .replace(/đ/g, "d")
      .replace(/[^a-z0-9\s-]/g, "") // Xóa ký tự đặc biệt
      .replace(/\s+/g, "_") // Đổi khoảng trắng thành gạch dưới
      .replace(/-+/g, "_");
    setProjName(slug);
  };

  return (
    <div className="p-10 max-w-5xl mx-auto w-full">
      <header className="mb-12">
        <h1 className="text-4xl font-black mb-4">📍 Trạm 1: Sáng Tác Kịch Bản</h1>
        <p className="text-slate-400 text-lg">Cỗ máy sẽ phân tích ý tưởng của bạn, tự động lên Kịch Bản Phân Cảnh chi tiết theo chuẩn Hollywood.</p>
      </header>

      <div className="glass-panel p-8 rounded-3xl">
        <div className="space-y-8">
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2 uppercase tracking-wide">Tên Dự Án (Không Dấu)</label>
            <input 
              type="text" 
              className="w-full bg-black/20 border border-white/10 rounded-xl px-5 py-4 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all placeholder:text-slate-600"
              placeholder="VD: bi_mat_vu_tru"
              value={projName}
              onChange={(e) => handleNameChange(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2 uppercase tracking-wide">Ý Tưởng Sáng Tác</label>
            <textarea 
              className="w-full h-48 bg-black/20 border border-white/10 rounded-xl px-5 py-4 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all placeholder:text-slate-600 resize-none"
              placeholder="Kể về một phi hành gia vô tình lạc vào lỗ đen vũ trụ..."
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
            />
          </div>

          <label className="flex items-center space-x-3 cursor-pointer group">
            <div className={`w-6 h-6 rounded border flex items-center justify-center transition-colors ${factCheck ? 'bg-blue-500 border-blue-500' : 'border-white/20 group-hover:border-white/40'}`}>
              {factCheck && <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>}
            </div>
            <input type="checkbox" className="hidden" checked={factCheck} onChange={(e) => setFactCheck(e.target.checked)} />
            <span className="text-slate-300 font-medium select-none group-hover:text-white transition-colors">
              🔍 Bật Chế độ &apos;Khảo Cổ&apos; (Ép AI kiểm chứng Sự thật Lịch sử/Khoa học 100%)
            </span>
          </label>

          <div className="pt-4">
            <button 
              onClick={handleSubmit}
              disabled={status === "loading" || !projName || !idea}
              className={`w-full py-5 rounded-2xl font-bold text-lg flex items-center justify-center gap-3 transition-all ${
                status === "loading" ? "bg-slate-800 text-slate-400 cursor-not-allowed" : 
                status === "success" ? "bg-green-500 text-white shadow-[0_0_20px_rgba(34,197,94,0.4)]" : 
                "btn-primary text-white"
              }`}
            >
              {status === "idle" && "🚀 Nạp Kịch Bản Tự Động"}
              {status === "loading" && (
                <>
                  <div className="w-6 h-6 border-3 border-white/20 border-t-white rounded-full animate-spin"></div>
                  Đang Gửi Lên Hệ Thống Lõi...
                </>
              )}
              {status === "success" && "✅ Đã nạp thành công! Chuyển sang Trạm 2"}
            </button>
          </div>
        </div>
      </div>
      
      <LiveDashboard />
    </div>
  );
}

function LiveDashboard() {
  const [liveStatus, setLiveStatus] = useState({ progress: 0, phase: "Chưa Khởi Động", log: "Đang chờ dữ liệu từ Hệ Thống Lõi..." });

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch("/api/stats");
        if (res.ok) {
          const data = await res.json();
          setLiveStatus(prev => ({
            progress: data.progress ?? prev.progress,
            phase: data.phase || prev.phase,
            log: data.log || prev.log,
          }));
        }
      } catch {
        // Silent fail on connect error
      }
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="mt-12 bg-slate-900/50 border border-blue-500/30 rounded-2xl p-6 shadow-[0_0_30px_rgba(59,130,246,0.1)] backdrop-blur-sm">
      <div className="flex justify-between items-end mb-4">
        <div>
          <h3 className="text-blue-400 font-bold uppercase tracking-wider text-xs mb-1">Live Dashboard</h3>
          <p className="text-white font-medium text-lg">{liveStatus.phase}</p>
        </div>
        <div className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300">
          {liveStatus.progress}%
        </div>
      </div>
      
      <div className="h-3 w-full bg-slate-800 rounded-full overflow-hidden mb-4 border border-slate-700/50">
        <div 
          className="h-full bg-gradient-to-r from-blue-600 to-cyan-400 transition-all duration-500 ease-out relative"
          style={{ width: `${liveStatus.progress}%` }}
        >
          <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
        </div>
      </div>
      
      <div className="bg-black/40 rounded-xl p-3 border border-white/5 font-mono text-sm text-green-400 flex items-start gap-2 h-20 overflow-hidden">
        <span className="text-slate-500 mt-0.5">{'>'}</span>
        <span className="break-words line-clamp-3">{liveStatus.log}</span>
      </div>
    </div>
  );
}
