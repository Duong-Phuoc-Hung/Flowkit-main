"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/", label: "📍 Trạm 1: Sáng Tác" },
  { href: "/tram-2", label: "⚖️ Trạm 2: Duyệt Kịch Bản" },
  { href: "/tram-2-5", label: "🖼️ Trạm 2.5: Duyệt Ảnh Tĩnh" },
  { href: "/tram-3", label: "📊 Trạm 3: Live Dashboard" },
  { href: "/tram-4", label: "🎧 Trạm 4: Bàn Mix & Xuất" },
  { href: "/tram-5", label: "🖼️ Trạm 5: Bơm View SEO" },
];

const TOOL_ITEMS = [
  { href: "/cau-hinh", label: "⚙️ Cấu Hình Máy (Kloning)" },
  { href: "/ai-phan-tich", label: "📈 AI Phân Tích (Học Máy)" },
  { href: "/diep-vien", label: "🕵️ Điệp Viên Cài Cắm" },
];

export default function Sidebar() {
  const pathname = usePathname();

  const renderLink = (item: { href: string; label: string }) => {
    const isActive = pathname === item.href;
    return (
      <Link
        key={item.href}
        href={item.href}
        className={`block px-4 py-3 rounded-xl transition-all duration-200 flex items-center justify-between group ${
          isActive
            ? "bg-gradient-to-r from-blue-600/30 to-purple-600/30 border border-blue-500/40 text-white font-bold shadow-[0_0_15px_rgba(59,130,246,0.25)]"
            : "hover:bg-white/10 text-slate-400 hover:text-white font-medium"
        }`}
      >
        <span>{item.label}</span>
        {isActive && (
          <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping shadow-[0_0_8px_#3b82f6]" />
        )}
      </Link>
    );
  };

  return (
    <aside className="w-64 flex-shrink-0 glass-panel border-r border-slate-800 flex flex-col">
      <div className="p-6">
        <h1 className="text-2xl font-black bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-pink-500">
          FlowKit SaaS
        </h1>
        <p className="text-xs text-slate-400 mt-1 uppercase tracking-widest font-semibold">
          V13.0 Masterpiece
        </p>
      </div>

      <nav className="flex-1 px-4 space-y-1.5 mt-2 overflow-y-auto custom-scrollbar">
        {NAV_ITEMS.map(renderLink)}

        <div className="pt-5 pb-2">
          <p className="text-[11px] font-extrabold text-slate-500 uppercase tracking-wider px-4">
            Siêu Công Cụ AI
          </p>
        </div>

        {TOOL_ITEMS.map(renderLink)}
      </nav>

      <div className="p-4 mt-auto">
        <div className="glass-panel p-4 rounded-xl text-sm border border-slate-800/80">
          <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Node Status</p>
          <div className="flex items-center gap-2 mt-2">
            <span className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse shadow-[0_0_10px_#22c55e]" />
            <span className="font-bold text-green-400 text-sm">Online</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
