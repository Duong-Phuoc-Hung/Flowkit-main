"use client";

import { useState, useEffect } from "react";

export default function Tram5() {
  const [projects, setProjects] = useState<string[]>([]);
  const [selectedProj, setSelectedProj] = useState("");
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState("");

  useEffect(() => {
    fetch('/api/tram5')
      .then(res => res.json())
      .then(data => setProjects(data.projects || []));
  }, []);

  const handleAction = async (action: string) => {
    if (!selectedProj) return alert("Vui lòng chọn dự án!");
    setLoading(true);
    setLogs(`Đang chạy ${action === 'seo' ? 'Phân tích SEO' : 'Máy tạo Ảnh Bìa'}...\n`);
    
    try {
      const res = await fetch('/api/tram5', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slug: selectedProj, action })
      });
      const data = await res.json();
      setLogs(prev => prev + "\n" + data.message);
    } catch {
      setLogs(prev => prev + "\n[!] LỖI KẾT NỐI");
    }
    setLoading(false);
  };

  return (
    <div className="p-10 max-w-5xl mx-auto w-full">
      <header className="mb-12">
        <h1 className="text-4xl font-black mb-4">🖼️ Trạm 5: Cỗ Máy "Bơm" View</h1>
        <p className="text-slate-400 text-lg">Tự động thiết kế Thumbnail giật gân và viết Mô tả chuẩn SEO để leo Top Trending.</p>
      </header>

      <div className="glass-panel p-8 rounded-3xl mb-8">
        <h2 className="text-2xl font-bold text-white mb-6">Chọn Video Đã Hoàn Thành</h2>
        <select 
          className="w-full bg-black/40 border border-white/20 rounded-xl px-5 py-4 text-white focus:outline-none focus:border-blue-500 mb-6"
          value={selectedProj}
          onChange={e => setSelectedProj(e.target.value)}
        >
          <option value="">-- Click để Chọn Dự án --</option>
          {projects.map(p => <option key={p} value={p}>{p}</option>)}
        </select>

        <div className="grid grid-cols-2 gap-6">
          <button 
            disabled={loading || !selectedProj}
            onClick={() => handleAction('thumbnail')}
            className="bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-bold py-4 rounded-xl shadow-lg transition-colors flex items-center justify-center gap-2"
          >
            🎨 Tạo Ảnh Bìa (Thumbnail) Siêu Cấp
          </button>
          
          <button 
            disabled={loading || !selectedProj}
            onClick={() => handleAction('seo')}
            className="bg-green-600 hover:bg-green-500 disabled:opacity-50 text-white font-bold py-4 rounded-xl shadow-lg transition-colors flex items-center justify-center gap-2"
          >
            📈 Viết Tiêu Đề & Mô Tả Chuẩn SEO
          </button>
        </div>
      </div>

      <div className="glass-panel p-6 rounded-3xl">
        <h3 className="text-xl font-bold text-slate-300 mb-4">Trạm Phân Tích Kỹ Thuật</h3>
        <pre className="bg-black/60 p-4 rounded-xl text-green-400 font-mono text-sm h-64 overflow-y-auto border border-white/5 whitespace-pre-wrap">
          {logs || "Chưa có tiến trình nào chạy..."}
        </pre>
      </div>
    </div>
  );
}
