"use client";

import { useState, useEffect, useRef, useCallback } from "react";

interface QueueStats {
  PENDING: number;
  PROCESSING: number;
  COMPLETED: number;
  FAILED: number;
}

interface DashboardStats {
  phase: string;
  progress: number;
  log: string;
  queue: QueueStats;
}

type WsStatus = "connecting" | "live" | "offline";

const WS_URL = "ws://127.0.0.1:8100/ws/dashboard";
const BACKOFF_STEPS = [1000, 2000, 4000, 8000, 16000, 30000];

export default function Tram3() {
  const [stats, setStats] = useState<DashboardStats>({
    phase: "", progress: 0, log: "",
    queue: { PENDING: 0, PROCESSING: 0, COMPLETED: 0, FAILED: 0 },
  });
  const [wsStatus, setWsStatus] = useState<WsStatus>("connecting");
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const retryRef = useRef(0);
  const retryTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  // Fallback HTTP poll when WS is offline
  const pollHttp = useCallback(async () => {
    try {
      const res = await fetch("/api/stats");
      if (res.ok) {
        const data = await res.json();
        if (mountedRef.current) {
          setStats(data);
          setLastUpdate(new Date());
        }
      }
    } catch { /* silent — WS reconnect handles recovery */ }
  }, []);

  const connect = useCallback(() => {
    if (!mountedRef.current) return;
    setWsStatus("connecting");

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      if (!mountedRef.current) return;
      retryRef.current = 0;
      setWsStatus("live");
    };

    ws.onmessage = (evt) => {
      if (!mountedRef.current) return;
      try {
        const msg = JSON.parse(evt.data as string);
        if (msg.type === "ping") return;
        // snapshot from /ws/dashboard sends {type:"snapshot", ...}
        // worker_tick events send {type:"worker_tick", active, slots, pending}
        if (msg.type === "snapshot" || msg.phase !== undefined || msg.queue) {
          setStats(prev => ({
            phase: msg.phase ?? prev.phase,
            progress: msg.progress ?? prev.progress,
            log: msg.log ?? prev.log,
            queue: msg.queue ?? prev.queue,
          }));
          setLastUpdate(new Date());
        }
        // Supplement: also re-poll HTTP for status.json data (lightweight)
        pollHttp();
      } catch { /* ignore malformed */ }
    };

    ws.onerror = () => { /* onclose will fire next */ };

    ws.onclose = () => {
      if (!mountedRef.current) return;
      setWsStatus("offline");
      wsRef.current = null;
      // Exponential backoff reconnect
      const delay = BACKOFF_STEPS[Math.min(retryRef.current, BACKOFF_STEPS.length - 1)];
      retryRef.current += 1;
      retryTimerRef.current = setTimeout(connect, delay);
    };
  }, [pollHttp]);

  useEffect(() => {
    mountedRef.current = true;
    // Initial HTTP poll so data shows immediately before WS connects
    pollHttp();
    connect();

    // While offline, keep polling HTTP every 3s as fallback
    const httpFallback = setInterval(() => {
      if (wsStatus !== "live") pollHttp();
    }, 3000);

    return () => {
      mountedRef.current = false;
      clearInterval(httpFallback);
      if (retryTimerRef.current) clearTimeout(retryTimerRef.current);
      wsRef.current?.close();
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const statusBadge: Record<WsStatus, { label: string; color: string; dot: string }> = {
    live:       { label: "🟢 Live",       color: "text-green-400",  dot: "bg-green-400 animate-pulse" },
    connecting: { label: "🟡 Đang kết nối", color: "text-yellow-400", dot: "bg-yellow-400 animate-ping" },
    offline:    { label: "🔴 Offline",    color: "text-red-400",    dot: "bg-red-400" },
  };
  const badge = statusBadge[wsStatus];

  return (
    <div className="p-10 max-w-7xl mx-auto w-full">
      <header className="mb-12">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-4xl font-black">📊 Trạm 3: Lõi Database (Bảng Thống Kê Live)</h1>
          <div className="flex items-center gap-2 glass-panel px-4 py-2 rounded-xl">
            <span className={`w-2 h-2 rounded-full ${badge.dot}`} />
            <span className={`text-sm font-bold ${badge.color}`}>{badge.label}</span>
          </div>
        </div>
        <p className="text-slate-400 text-lg">
          Bảng điều khiển theo dõi tiến độ công việc và trạng thái hàng đợi của AI.
          {lastUpdate && (
            <span className="ml-2 text-slate-600 text-sm">
              Cập nhật: {lastUpdate.toLocaleTimeString("vi-VN")}
            </span>
          )}
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Trạng thái máy sản xuất */}
        <div className="lg:col-span-2 glass-panel p-8 rounded-3xl">
          <h3 className="text-2xl font-bold text-white mb-6">Trạng Thái Máy Sản Xuất</h3>
          <div className="mb-4">
            <span className="text-slate-400 font-bold uppercase text-sm block mb-1">Giai Đoạn Hiện Tại:</span>
            <span className="text-blue-400 font-bold text-xl">{stats.phase || "Đang Nghỉ Ngơi"}</span>
          </div>

          <div className="w-full bg-slate-800 rounded-full h-4 mb-4 overflow-hidden border border-slate-700">
            <div
              className="bg-gradient-to-r from-blue-500 to-purple-500 h-4 rounded-full transition-all duration-700"
              style={{ width: `${stats.progress}%` }}
            />
          </div>

          <div className="bg-black/30 p-4 rounded-xl border border-white/5 font-mono text-sm text-green-400 min-h-[60px]">
            {stats.log || "Hệ thống sẵn sàng..."}
          </div>

          {/* WS offline warning */}
          {wsStatus === "offline" && (
            <div className="mt-4 bg-red-500/10 border border-red-500/30 rounded-xl p-3 text-red-400 text-sm flex items-center gap-2">
              ⚠️ Mất kết nối WebSocket — đang dùng HTTP fallback. Tự động kết nối lại...
            </div>
          )}
        </div>

        {/* Hàng đợi */}
        <div className="glass-panel p-8 rounded-3xl">
          <h3 className="text-2xl font-bold text-white mb-6">Hàng Đợi Google Flow</h3>
          <div className="space-y-4">
            {[
              { icon: "⏳", label: "Đang Xếp Hàng",   key: "PENDING",    color: "text-yellow-500" },
              { icon: "⚙️", label: "Đang Vẽ/Dựng",    key: "PROCESSING", color: "text-blue-500"   },
              { icon: "✅", label: "Đã Hoàn Thành",   key: "COMPLETED",  color: "text-green-500"  },
              { icon: "❌", label: "Bị Lỗi (Thử lại)", key: "FAILED",     color: "text-red-500"    },
            ].map(({ icon, label, key, color }) => (
              <div key={key} className="bg-black/20 p-4 rounded-xl flex justify-between items-center border border-white/5">
                <span className="text-slate-300 flex items-center gap-2">
                  <span>{icon}</span> {label}
                </span>
                <span className={`text-2xl font-black ${color} tabular-nums`}>
                  {stats.queue[key as keyof QueueStats]}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
