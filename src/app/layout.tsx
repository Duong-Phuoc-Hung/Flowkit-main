import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import Sidebar from "@/components/Sidebar";
import "./globals.css";

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "FlowKit Enterprise SaaS",
  description: "AI-powered video generation studio",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" className="dark" suppressHydrationWarning>
      <body className={`${outfit.variable} antialiased flex h-screen bg-[#0f172a] text-slate-200 overflow-hidden`} suppressHydrationWarning>
        <Sidebar />
        
        {/* Main Content */}
        <main className="flex-1 flex flex-col h-full relative overflow-y-auto custom-scrollbar">
          {children}
        </main>
      </body>
    </html>
  );
}
