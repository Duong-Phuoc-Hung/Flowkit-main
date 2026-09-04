"use client";

import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center p-10">
      <div className="text-center max-w-lg">
        <div className="text-8xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-purple-500 mb-4">
          404
        </div>
        <h1 className="text-3xl font-bold text-white mb-4">Không Tìm Thấy Trang</h1>
        <p className="text-slate-400 text-lg mb-8">
          Trang bạn tìm kiếm không tồn tại hoặc đã bị di chuyển.
        </p>
        <Link
          href="/"
          className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600
                     hover:from-blue-500 hover:to-purple-500 text-white font-bold py-3 px-8
                     rounded-2xl transition-all duration-300 hover:scale-105"
        >
          🏠 Về Trạm 1
        </Link>
      </div>
    </div>
  );
}
