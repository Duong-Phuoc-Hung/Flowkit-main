"use client";

import { useState, useEffect } from "react";

export default function AiPhanTich() {
  const [rules, setRules] = useState("Đang tải...");
  const [file, setFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    fetch('/api/analyze')
      .then(res => res.json())
      .then(data => setRules(data.rules || "Chưa có quy luật nào."))
      .catch(() => setRules("Lỗi tải quy luật."));
  }, []);

  const handleAnalyze = async () => {
    if (!file) {
      alert("Vui lòng chọn 1 ảnh biểu đồ.");
      return;
    }
    
    setAnalyzing(true);
    const formData = new FormData();
    formData.append('image', file);

    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      
      if (res.ok) {
        setRules(data.rules);
        setFile(null);
        alert("Đã hấp thụ quy luật mới!");
      } else {
        alert("Lỗi: " + data.error);
      }
    } catch {
      alert("Lỗi kết nối.");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="p-10 max-w-5xl mx-auto w-full">
      <header className="mb-12">
        <h1 className="text-4xl font-black mb-4">📈 AI Phân Tích Dữ Liệu (Self-Learning)</h1>
        <p className="text-slate-400 text-lg">Chụp ảnh bảng Thống kê YouTube/TikTok để Mắt thần Vision AI rút ra quy luật tăng view.</p>
      </header>

      <div className="glass-panel p-8 rounded-3xl mb-8 border border-blue-500/30">
        <h3 className="font-bold text-blue-400 mb-4 flex items-center gap-2">
          <span>🧠</span> BỘ LUẬT KIẾM TIỀN HIỆN TẠI TRONG NÃO AI:
        </h3>
        <p className="text-slate-200 whitespace-pre-wrap leading-relaxed">{rules}</p>
      </div>

      <div className="glass-panel p-8 rounded-3xl">
        <h3 className="text-2xl font-bold text-white mb-6">Tải Lên Biểu Đồ Mới</h3>
        <input 
          type="file" 
          accept="image/png, image/jpeg" 
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="block w-full text-sm text-slate-400
            file:mr-4 file:py-3 file:px-6
            file:rounded-xl file:border-0
            file:text-sm file:font-bold
            file:bg-blue-500/20 file:text-blue-400
            hover:file:bg-blue-500/30 mb-6 cursor-pointer"
        />
        
        <button 
          onClick={handleAnalyze}
          disabled={analyzing || !file}
          className={`w-full py-4 rounded-xl font-bold transition-all ${analyzing ? 'bg-slate-700 text-slate-400 cursor-not-allowed' : 'btn-primary text-white shadow-[0_0_15px_rgba(59,130,246,0.4)]'}`}
        >
          {analyzing ? '🧠 Mắt thần AI đang đọc và suy nghĩ (Vui lòng đợi)...' : '🚀 Phân Tích & Nâng Cấp Não Bộ'}
        </button>
      </div>
    </div>
  );
}
