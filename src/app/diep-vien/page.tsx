"use client";

import { useState } from "react";

export default function DiepVien() {
  const [url, setUrl] = useState("");
  const [topic, setTopic] = useState("");
  const [spying, setSpying] = useState(false);
  const [result, setResult] = useState<Record<string, string> | null>(null);

  const handleSpy = async () => {
    if (!url || !topic) {
      alert("Vui lòng nhập Link và Chủ đề.");
      return;
    }
    
    setSpying(true);
    setResult(null);

    try {
      const res = await fetch('/api/spy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, topic })
      });
      const data = await res.json();
      
      if (res.ok) {
        setResult(data);
        alert("Nhiệm vụ Đánh cắp hoàn tất! Kịch bản đã được bơm thẳng vào Trạm 1.");
      } else {
        alert("Lỗi: " + data.error);
      }
    } catch {
      alert("Lỗi kết nối.");
    } finally {
      setSpying(false);
    }
  };

  return (
    <div className="p-10 max-w-5xl mx-auto w-full">
      <header className="mb-12">
        <h1 className="text-4xl font-black mb-4">🕵️ Điệp Viên Cài Cắm (Clone Đối Thủ)</h1>
        <p className="text-slate-400 text-lg">Phân tích video của đối thủ để bóc tách công thức thành công và tự động viết kịch bản mới.</p>
      </header>

      <div className="glass-panel p-8 rounded-3xl mb-8">
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2 uppercase tracking-wide">🔗 Link YouTube / TikTok của đối thủ:</label>
            <input 
              type="text" 
              className="w-full bg-black/20 border border-white/10 rounded-xl px-5 py-4 text-white focus:outline-none focus:border-blue-500"
              placeholder="https://youtube.com/watch?v=..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2 uppercase tracking-wide">💡 Chủ đề bạn muốn làm:</label>
            <input 
              type="text" 
              className="w-full bg-black/20 border border-white/10 rounded-xl px-5 py-4 text-white focus:outline-none focus:border-blue-500"
              placeholder="Ví dụ: Sự thật về loài chuột"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            />
          </div>
          <button 
            onClick={handleSpy}
            disabled={spying || !url || !topic}
            className={`w-full py-4 rounded-xl font-bold transition-all ${spying ? 'bg-slate-700 text-slate-400 cursor-not-allowed' : 'bg-red-500 hover:bg-red-600 text-white shadow-[0_0_15px_rgba(239,68,68,0.4)]'}`}
          >
            {spying ? '🕵️ Điệp viên đang tải trộm âm thanh và viết kịch bản (Đợi 1-2 phút)...' : '🚀 Bắt Đầu Đánh Cắp Ý Tưởng'}
          </button>
        </div>
      </div>

      {result && (
        <div className="glass-panel p-8 rounded-3xl border border-green-500/30">
          <h3 className="text-2xl font-bold text-green-400 mb-4 flex items-center gap-2">
            <span>✅</span> CHIẾN LỢI PHẨM THU ĐƯỢC
          </h3>
          <div className="mb-4">
            <span className="text-slate-400 font-bold uppercase text-sm">Mã Kịch Bản Sinh Ra: </span>
            <span className="text-white font-mono bg-white/10 px-2 py-1 rounded">{result.project}</span>
          </div>
          <div>
            <span className="text-slate-400 font-bold uppercase text-sm block mb-2">Quy Luật Ăn Cắp Được: </span>
            <p className="text-slate-200 bg-black/20 p-4 rounded-xl leading-relaxed">{result.rules}</p>
          </div>
        </div>
      )}
    </div>
  );
}
