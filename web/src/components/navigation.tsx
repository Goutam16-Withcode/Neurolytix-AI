'use client';

import React from 'react';
import { 
  Brain, 
  Database, 
  Sparkles, 
  Cpu, 
  Scale, 
  FileText, 
  Sliders, 
  CheckCircle2, 
  MessageSquareCode
} from 'lucide-react';
import { ShimmerBadge } from '@/components/ui/shimmer-badge';
import { DatasetInfo } from '@/types';

interface NavigationProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  dataset: DatasetInfo | null;
  proMode: boolean;
  setProMode: (pro: boolean) => void;
  onOpenCopilot: () => void;
}

export function Navigation({
  activeTab,
  setActiveTab,
  dataset,
  proMode,
  setProMode,
  onOpenCopilot,
}: NavigationProps) {
  const tabs = [
    { id: 'bento', label: 'Bento Hub', icon: Sparkles },
    { id: 'data', label: 'Data Studio', icon: Database },
    { id: 'automl', label: 'AutoML Tournament', icon: Cpu },
    { id: 'jev', label: 'Agentic RAG & JEV', icon: Scale, highlight: true },
    { id: 'reports', label: 'Executive Reports', icon: FileText },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200/80 bg-white/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-md shadow-indigo-500/20 text-white">
              <Brain className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-xl tracking-tight text-slate-900 font-outfit">
                  Neurolytix<span className="text-indigo-600">.AI</span>
                </span>
                <ShimmerBadge variant="indigo" className="text-[10px] py-0.5">
                  Studio 2.0
                </ShimmerBadge>
              </div>
              <p className="text-[11px] text-slate-500 font-medium">AutoML & Agentic Decision Intelligence</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden md:flex items-center gap-1.5 bg-slate-100/70 p-1 rounded-xl border border-slate-200/60">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 ${
                    isActive
                      ? 'bg-white text-indigo-600 shadow-sm shadow-slate-200 font-bold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
                  }`}
                >
                  <Icon className={`h-4 w-4 ${isActive ? 'text-indigo-600' : 'text-slate-500'}`} />
                  <span>{tab.label}</span>
                  {tab.highlight && (
                    <span className="h-1.5 w-1.5 rounded-full bg-cyan-500 animate-pulse" />
                  )}
                </button>
              );
            })}
          </nav>

          {/* Right Action Items */}
          <div className="flex items-center gap-3">
            {/* Active Dataset Pill */}
            {dataset ? (
              <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded-lg bg-emerald-50/80 border border-emerald-200 text-emerald-800 text-xs font-medium">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                <span className="max-w-[130px] truncate">{dataset.name}</span>
                <span className="text-emerald-600 font-bold">({dataset.rows.toLocaleString()} rows)</span>
              </div>
            ) : (
              <div className="hidden lg:flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-100 text-slate-500 text-xs font-medium">
                <Database className="h-3.5 w-3.5" />
                <span>No Data Loaded</span>
              </div>
            )}

            {/* Pro Mode Switch */}
            <div className="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-slate-50 border border-slate-200/80 text-xs">
              <Sliders className="h-3.5 w-3.5 text-slate-500" />
              <span className="text-slate-600 font-medium hidden sm:inline">Pro Mode</span>
              <button
                onClick={() => setProMode(!proMode)}
                className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                  proMode ? 'bg-indigo-600' : 'bg-slate-300'
                }`}
              >
                <span
                  className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                    proMode ? 'translate-x-4' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>

            {/* AI Copilot Button */}
            <button
              onClick={onOpenCopilot}
              className="relative group flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-700 text-white text-xs font-semibold shadow-md shadow-indigo-500/20 hover:from-indigo-500 hover:to-indigo-600 transition-all cursor-pointer overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
              <MessageSquareCode className="h-3.5 w-3.5" />
              <span>Ask AI Copilot</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
