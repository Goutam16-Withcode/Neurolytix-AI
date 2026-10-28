'use client';

import React from 'react';
import { Sparkles, Zap, ShieldCheck, Trophy, Layers } from 'lucide-react';

export interface StatItem {
  value: string;
  label: string;
  description: string;
}

interface StatsWithGradientProps {
  title?: string;
  subtitle?: string;
  stats?: StatItem[];
  className?: string;
}

export function StatsWithGradient({
  title = "Engineered for autonomous intelligence at scale",
  subtitle = "Built by machine learning engineers and decision theorists to eliminate manual data wrangling, black-box pipelines, and hallucinations.",
  stats,
  className = "",
}: StatsWithGradientProps) {
  const defaultStats: StatItem[] = stats || [
    {
      value: "< 10ms",
      label: "Real-Time Inference",
      description: "Sub-10ms latency deployed via FastAPI. Includes instant live simulator and production cURL endpoints.",
    },
    {
      value: "94.8%",
      label: "Champion ROC-AUC",
      description: "Top tournament score attained by CatBoost and LightGBM suites across customer churn benchmarks.",
    },
    {
      value: "100%",
      label: "Hallucination-Free",
      description: "Grounded by JEV Multi-Agent Verifier Shield. Every recommendation cites audited dataset columns.",
    },
    {
      value: "6+ Models",
      label: "Autonomous Algorithms",
      description: "Native Tabular ML, Prophet Time-Series & NLP Text Classifiers. Computer Vision (CV) completely removed.",
    },
  ];

  return (
    <section className={`relative w-full py-24 px-4 overflow-hidden ${className}`}>
      {/* Diagonal Striped Background Pattern (Matches Image 2) */}
      <div 
        className="absolute inset-0 pointer-events-none opacity-[0.07]"
        style={{
          backgroundImage: `repeating-linear-gradient(
            -45deg,
            rgba(255, 255, 255, 0.4) 0,
            rgba(255, 255, 255, 0.4) 1px,
            transparent 0,
            transparent 12px
          )`
        }}
      />

      {/* Atmospheric Diffuse Bottom Purple/Sapphire Glow (Matches Image 2) */}
      <div className="absolute -bottom-32 inset-x-0 h-96 bg-gradient-to-t from-purple-700/35 via-blue-600/20 to-transparent blur-[120px] pointer-events-none rounded-full" />

      <div className="relative z-10 max-w-6xl mx-auto text-center">
        {/* Title & Subtitle */}
        <h2 className="text-3xl sm:text-4xl md:text-5xl font-black font-outfit text-white tracking-tight leading-tight max-w-3xl mx-auto">
          {title}
        </h2>
        <p className="mt-4 text-sm sm:text-base text-slate-300 max-w-2xl mx-auto leading-relaxed">
          {subtitle}
        </p>

        {/* 4 Stats Cards Grid (Exact Visual Match to Image 2) */}
        <div className="mt-14 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-left">
          {defaultStats.map((item, idx) => (
            <div
              key={idx}
              className="p-6 rounded-2xl bg-[#080B14]/85 border border-white/10 backdrop-blur-xl shadow-[0_15px_35px_rgba(0,0,0,0.8)] hover:border-blue-500/40 hover:bg-[#0A0E1C]/90 transition-all duration-300 group flex flex-col justify-between"
            >
              <div>
                <span className="text-3xl sm:text-4xl font-black font-outfit text-white tracking-tight group-hover:text-blue-300 transition-colors">
                  {item.value}
                </span>
                <p className="text-xs font-bold text-blue-400 font-mono mt-1 uppercase tracking-wider">
                  {item.label}
                </p>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed mt-4">
                {item.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
