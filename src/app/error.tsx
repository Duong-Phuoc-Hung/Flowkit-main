"use client";

import { useEffect } from "react";
import Link from "next/link";

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function Error({ error, reset }: ErrorProps) {
  useEffect(() => {
    console.error("[FlowKit Error]", error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center p-10">
      <div className="text-center max-w-lg glass-panel p-10 rounded-3xl">
        <div className="text-7xl mb-6">⚠️</div>
        <h1 className="text-3xl font-bold text-white mb-4">Có Lỗi Xảy Ra</h1>
        <p className="text-slate-400 text-lg mb-2">
          Một lỗi không mong muốn đã xảy ra trong trang này.
        </p>
        {error?.digest && (
          <p className="text-slate-600 text-xs font-mono mb-6">
            ID: {error.digest}
          </p>
        )}
        <div className="flex gap-4 justify-center">
          <button
            onClick={reset}
            className="bg-gradient-to-r from-blue-600 to-purple-600
                       hover:from-blue-500 hover:to-purple-500 text-white font-bold
                       py-3 px-6 rounded-2xl transition-all duration-300 hover:scale-105"
          >
            🔄 Thử Lại
          </button>
          <Link
            href="/"
            className="border border-slate-600 hover:border-slate-400 text-slate-300
                       hover:text-white font-bold py-3 px-6 rounded-2xl
                       transition-all duration-300"
          >
            🏠 Về Trang Chủ
          </Link>
        </div>
      </div>
    </div>
  );
}
