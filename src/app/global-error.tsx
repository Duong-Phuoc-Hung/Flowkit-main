"use client";

interface GlobalErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function GlobalError({ error, reset }: GlobalErrorProps) {
  return (
    <html lang="vi">
      <body style={{ margin: 0, background: "#0a0a1a", fontFamily: "system-ui, sans-serif" }}>
        <div style={{
          minHeight: "100vh", display: "flex", alignItems: "center",
          justifyContent: "center", padding: "2.5rem",
        }}>
          <div style={{ textAlign: "center", maxWidth: "32rem" }}>
            <div style={{ fontSize: "5rem", marginBottom: "1rem" }}>💥</div>
            <h1 style={{ fontSize: "2rem", fontWeight: 900, color: "#fff", marginBottom: "1rem" }}>
              Lỗi Nghiêm Trọng
            </h1>
            <p style={{ color: "#94a3b8", fontSize: "1.1rem", marginBottom: "0.5rem" }}>
              Ứng dụng gặp lỗi không thể phục hồi. Vui lòng tải lại trang.
            </p>
            {error?.digest && (
              <p style={{ color: "#475569", fontSize: "0.75rem", fontFamily: "monospace", marginBottom: "1.5rem" }}>
                ID: {error.digest}
              </p>
            )}
            <button
              onClick={reset}
              style={{
                background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
                color: "#fff", fontWeight: 700, padding: "0.75rem 2rem",
                borderRadius: "1rem", border: "none", cursor: "pointer",
                fontSize: "1rem",
              }}
            >
              🔄 Tải Lại Ứng Dụng
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
