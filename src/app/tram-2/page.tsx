"use client";

import { useState, useEffect } from "react";

interface Scene {
  prompt: string;
  voice_gender: string;
  narrator_text: string;
}

interface ProjectData {
  scenes?: Scene[];
}

interface Project {
  slug: string;
  data: ProjectData;
}

export default function Tram2() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/pending')
      .then(res => res.json())
      .then(data => {
        setProjects(data.pending || []);
        setLoading(false);
      });
  }, []);

  const handleApprove = async (slug: string, currentData: ProjectData) => {
    try {
      const res = await fetch('/api/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slug, updatedData: currentData })
      });
      if (res.ok) {
        setProjects(projects.filter(p => p.slug !== slug));
        alert('Phê duyệt thành công! Máy AI đang vẽ ảnh.');
      } else {
        alert('Lỗi phê duyệt.');
      }
    } catch {
      alert('Lỗi kết nối.');
    }
  };

  const handleDelete = async (slug: string) => {
    if (!confirm(`Bạn có chắc chắn muốn hủy bỏ kịch bản ${slug}?`)) return;
    try {
      const res = await fetch('/api/pending', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slug }),
      });
      if (res.ok) {
        setProjects(projects.filter(p => p.slug !== slug));
      } else {
        alert('Lỗi khi xóa kịch bản.');
      }
    } catch {
      alert('Lỗi kết nối.');
    }
  };

  const handleUpdateScene = (slug: string, sIdx: number, field: string, value: string) => {
    setProjects(projects.map(p => {
      if (p.slug === slug && p.data.scenes) {
        const newScenes = [...p.data.scenes];
        newScenes[sIdx] = { ...newScenes[sIdx], [field]: value };
        return { ...p, data: { ...p.data, scenes: newScenes } };
      }
      return p;
    }));
  };

  const handleInsertScene = (slug: string, sIdx: number) => {
    setProjects(projects.map(p => {
      if (p.slug === slug && p.data.scenes) {
        const newScenes = [...p.data.scenes];
        newScenes.splice(sIdx + 1, 0, { prompt: "[Thêm mô tả cảnh tĩnh vào đây]", voice_gender: "Nữ", narrator_text: "" });
        return { ...p, data: { ...p.data, scenes: newScenes } };
      }
      return p;
    }));
  };

  const handleDeleteScene = (slug: string, sIdx: number) => {
    setProjects(projects.map(p => {
      if (p.slug === slug && p.data.scenes) {
        const newScenes = [...p.data.scenes];
        newScenes.splice(sIdx, 1);
        return { ...p, data: { ...p.data, scenes: newScenes } };
      }
      return p;
    }));
  };

  if (loading) {
    return <div className="p-10 flex items-center justify-center h-full"><div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div></div>;
  }

  return (
    <div className="p-10 max-w-7xl mx-auto w-full">
      <header className="mb-12 flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-black mb-4">⚖️ Trạm 2: Duyệt Kịch Bản (Storyboard)</h1>
          <p className="text-slate-400 text-lg">Kéo thả, chỉnh sửa trực quan kịch bản trước khi đẩy vào máy vẽ AI.</p>
        </div>
        <div className="text-right">
          <span className="bg-blue-500/20 text-blue-400 px-4 py-2 rounded-full font-bold text-sm">
            {projects.length} Dự án đang chờ duyệt
          </span>
        </div>
      </header>

      {projects.length === 0 ? (
        <div className="glass-panel p-16 rounded-3xl text-center border-dashed border-2 border-slate-700">
          <div className="text-6xl mb-4">📭</div>
          <h3 className="text-2xl font-bold text-slate-300">Kho lưu trữ trống</h3>
          <p className="text-slate-500 mt-2">Chưa có kịch bản nào được Sáng tác ở Trạm 1.</p>
        </div>
      ) : (
        <div className="space-y-10">
          {projects.map((proj, idx) => (
            <div key={idx} className="glass-panel p-8 rounded-3xl">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                  <span className="text-blue-500">📁</span> {proj.slug}
                </h2>
                <div className="flex gap-3">
                  <button onClick={() => handleDelete(proj.slug)} className="btn-danger text-white px-6 py-2 rounded-xl font-semibold text-sm">❌ Hủy Bỏ</button>
                  <button onClick={() => handleApprove(proj.slug, proj.data)} className="btn-primary text-white px-6 py-2 rounded-xl font-semibold text-sm shadow-[0_0_15px_rgba(59,130,246,0.5)]">✅ Phê Duyệt Toàn Bộ</button>
                </div>
              </div>
              
              {/* Horizontal Scrollable Storyboard */}
              <div className="flex overflow-x-auto gap-6 pb-6 snap-x">
                {proj.data?.scenes?.map((scene: Scene, sIdx: number) => (
                  <div key={sIdx} className="snap-center min-w-[320px] bg-black/40 border border-white/10 rounded-2xl p-5 flex-shrink-0 hover:border-blue-500/50 transition-colors group relative">
                    <div className="absolute -top-3 -left-3 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center font-black shadow-lg">
                      {sIdx + 1}
                    </div>
                    
                    <div className="mb-4 mt-2">
                      <label className="text-xs text-slate-500 font-bold uppercase tracking-wider mb-1 block">Góc Máy / Bối Cảnh</label>
                      <textarea 
                        className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-sm text-slate-200 h-24 resize-none focus:border-blue-500 outline-none"
                        value={scene.prompt}
                        onChange={(e) => handleUpdateScene(proj.slug, sIdx, 'prompt', e.target.value)}
                      />
                    </div>
                    
                    <div>
                      <label className="text-xs text-slate-500 font-bold uppercase tracking-wider mb-1 block">Lời Thoại (Kênh {scene.voice_gender || 'Nữ'})</label>
                      <textarea 
                        className="w-full bg-blue-500/10 border border-blue-500/20 rounded-lg p-3 text-sm text-blue-100 h-24 resize-none focus:border-blue-500 outline-none"
                        value={scene.narrator_text}
                        onChange={(e) => handleUpdateScene(proj.slug, sIdx, 'narrator_text', e.target.value)}
                      />
                    </div>
                    
                    <div className="mt-4 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button onClick={() => handleInsertScene(proj.slug, sIdx)} className="flex-1 bg-white/10 hover:bg-white/20 text-xs font-bold py-2 rounded-lg transition-colors">➕ Chèn Giữa</button>
                      <button onClick={() => handleDeleteScene(proj.slug, sIdx)} className="flex-1 bg-red-500/20 hover:bg-red-500/40 text-red-300 text-xs font-bold py-2 rounded-lg transition-colors">🗑️ Xóa</button>
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
