import type { Metadata } from "next";
import { Plus_Jakarta_Sans, Outfit } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
});

const jakarta = Plus_Jakarta_Sans({
  variable: "--font-jakarta",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "Neurolytix AI — Intelligent AutoML & Decision Intelligence Studio",
  description: "Next-generation automated machine learning, data intelligence, and Agentic RAG decision engine.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${outfit.variable} ${jakarta.variable} antialiased`}>
      <body className="min-h-screen bg-[#ffffff] text-slate-900 font-sans selection:bg-indigo-500/10 selection:text-indigo-600">
        {children}
      </body>
    </html>
  );
}
