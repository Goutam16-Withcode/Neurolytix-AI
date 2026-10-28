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
  MessageSquareCode,
  Activity,
  Wifi,
  WifiOff
} from 'lucide-react';
import { ShimmerBadge } from '@/components/ui/shimmer-badge';
import { DatasetInfo } from '@/types';
import { HealthStatus } from '@/lib/api';

interface NavigationProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  dataset: DatasetInfo | null;
  proMode: boolean;
  setProMode: (pro: boolean) => void;
  onOpenCopilot: () => void;
  backendHealth: HealthStatus;
}

export function Navigation({
  activeTab,
  setActiveTab,
  dataset,
  proMode,
  setProMode,
  onOpenCopilot,
  backendHealth,
}: NavigationProps) {
  const tabs = [
    { id: 'bento', label: 'Bento Hub', icon: Sparkles },
    { id: 'data', label: 'Data Studio', icon: Database },
    { id: 'automl', label: 'AutoML Tournament', icon: Cpu },
    { id: 'jev', label: 'Agentic RAG & JEV', icon: Scale, highlight: true },
    { id: 'reports', label: 'Executive Reports', icon: FileText },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white/95 backdrop-blur-md shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-700 to-cyan-500 flex items-center justify-center shadow-md shadow-indigo-600/20 text-white">
              <Brain className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-xl tracking-tight text-slate-900 font-outfit">
                  Neurolytix<span className="text-indigo-600">.AI</span>
                </span>
                <span className="px-2 py-0.5 rounded-md bg-indigo-50 border border-indigo-100 text-[10px] font-bold text-indigo-700">
                  Enterprise 2.0
                </span>
              </div>
              <p className="text-[11px] text-slate-500 font-medium">Automated ML & Decision Intelligence</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden md:flex items-center gap-1 bg-slate-100/90 p-1 rounded-xl border border-slate-200/80">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all duration-150 cursor-pointer ${
                    isActive
                      ? 'bg-white text-indigo-600 shadow-xs font-bold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-white/60'
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

          {/* Right Status & Actions */}
          <div className="flex items-center gap-3">
            {/* Live Backend Connection Indicator */}
            <div
              className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-semibold border ${
                backendHealth.online
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  : 'bg-amber-50 text-amber-700 border-amber-200'
              }`}
              title={backendHealth.online ? `FastAPI running on :8000 (${backendHealth.latencyMs}ms)` : 'FastAPI server offline'}
            >
              <span
                className={`h-2 w-2 rounded-full ${
                  backendHealth.online ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'
                }`}
              />
              <span>{backendHealth.online ? `API :8000 (${backendHealth.latencyMs}ms)` : 'API Offline'}</span>
            </div>

            {/* Active Dataset Pill */}
            {dataset ? (
              <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded-lg bg-slate-100 border border-slate-200 text-slate-700 text-xs font-medium">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                <span className="max-w-[120px] truncate">{dataset.name}</span>
                <span className="text-slate-500 font-bold">({dataset.rows.toLocaleString()} rows)</span>
              </div>
            ) : null}

            {/* Pro Mode Switch */}
            <div className="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-slate-50 border border-slate-200 text-xs">
              <Sliders className="h-3.5 w-3.5 text-slate-500" />
              <span className="text-slate-600 font-medium hidden sm:inline">Pro</span>
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
              className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-indigo-600 text-white text-xs font-semibold shadow-sm hover:bg-indigo-700 transition cursor-pointer"
            >
              <MessageSquareCode className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Ask AI</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
