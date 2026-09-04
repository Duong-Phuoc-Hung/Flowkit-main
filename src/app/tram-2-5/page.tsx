"use client";

import { useState, useEffect } from "react";

export default function Tram2_5() {
  const [projects, setProjects] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/tram25')
      .then(res => res.json())
      .then(data => {
        setProjects(data.pending || []);
        setLoading(false);
      });
  }, []);

  const handleRegen = async (scene_id: string, video_id: string) => {
    await fetch('/api/tram25', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'REGENERATE', scene_id, video_id })
    });
    alert('Đã gửi lệnh vẽ lại! Bạn vui lòng chờ vài phút.');
  };

  const handleApprove = async (slug: string) => {
    await fetch('/api/tram25', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'APPROVE', slug })
    });
    setProjects(projects.filter(p => p.slug !== slug));
    alert('Bức tranh hoàn hảo! Đã đẩy qua Trạm 4 dựng Video.');
  };

  if (loading) return <div className="p-10 flex justify-center"><div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div></div>;

  return (
    <div className="p-10 max-w-7xl mx-auto w-full">
      <header className="mb-12">
        <h1 className="text-4xl font-black mb-4">🖼️ Trạm 2.5: Duyệt Ảnh Tĩnh (Chống Lỗi)</h1>
        <p className="text-slate-400 text-lg">Soi kỹ từng bức ảnh do AI vẽ ra trước khi đưa vào chuyển động Video.</p>
      </header>

      {projects.length === 0 ? (
        <div className="glass-panel p-16 rounded-3xl text-center border-dashed border-2 border-slate-700">
          <div className="text-6xl mb-4">✨</div>
          <h3 className="text-2xl font-bold text-slate-300">Không có ảnh nào cần duyệt</h3>
        </div>
      ) : (
        <div className="space-y-10">
          {projects.map((proj, idx) => (
            <div key={idx} className="glass-panel p-8 rounded-3xl">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                  <span className="text-blue-500">📁</span> {proj.slug as string}
                </h2>
                <button onClick={() => handleApprove(proj.slug as string)} className="btn-primary text-white px-6 py-2 rounded-xl font-bold shadow-[0_0_15px_rgba(59,130,246,0.5)]">
                  🚀 Bức Tranh Hoàn Hảo (Dựng Video)
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {(proj.scenes as Record<string, unknown>[])?.map((scene: Record<string, unknown>, sIdx: number) => (
                  <div key={sIdx} className="bg-black/40 rounded-2xl overflow-hidden border border-white/10 group relative">
                    <div className="absolute top-2 left-2 bg-black/60 px-2 py-1 rounded text-xs font-bold text-white z-10">Cảnh {sIdx + 1}</div>
                    {scene.horizontal_image_url ? (
                      <div className="relative aspect-video">
                        <img src={scene.horizontal_image_url as string} alt="Scene" className="w-full h-full object-cover" />
                        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                          <button onClick={() => handleRegen(scene.id as string, (proj.data as Record<string, unknown>)?.video_id as string)} className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded-lg shadow-lg">
                            🖌️ Yêu Cầu Vẽ Lại
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="aspect-video flex items-center justify-center bg-slate-800 text-slate-500">
                        Đang vẽ...
                      </div>
                    )}
                    <div className="p-3">
                      <p className="text-xs text-slate-400 line-clamp-2">{scene.prompt as string}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
