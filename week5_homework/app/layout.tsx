import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";

const geist = Geist({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Week5 ML Lab",
  description: "AI & Deep Learning Interactive Demo — 부산대 전산물리",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className={`${geist.className} bg-gray-950 text-white min-h-screen`}>
        {children}
      </body>
    </html>
  );
}
