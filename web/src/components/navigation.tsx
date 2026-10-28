'use client';

import React from 'react';
import { 
  Compass,
  Database, 
  BarChart3, 
  BrainCircuit, 
  Rocket, 
  Scale, 
  FileText, 
  CheckCircle2, 
  MessageSquareCode,
  ArrowLeft,
  Activity,
  Layers
} from 'lucide-react';
import { DatasetInfo } from '@/types';
import { HealthStatus } from '@/lib/api';

interface NavigationProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  dataset: DatasetInfo | null;
  onOpenCopilot: () => void;
  backendHealth: HealthStatus;
  onBackToHome?: () => void;
}

export function Navigation({
  activeTab,
  setActiveTab,
  dataset,
  onOpenCopilot,
  backendHealth,
  onBackToHome,
}: NavigationProps) {
  const steps = [
    { id: 'data', label: '1. Ingest Data', icon: Database },
    { id: 'eda', label: '2. Dynamic EDA', icon: BarChart3 },
    { id: 'scientist', label: '3. Data Scientist', icon: BrainCircuit },
    { id: 'automl', label: '4. Model & Deploy', icon: Rocket },
    { id: 'jev', label: '5. JEV Decisions', icon: Scale },
    { id: 'reports', label: '6. Reports', icon: FileText },
  ];

  return (
    <header className="sticky top-3 z-50 max-w-7xl mx-auto px-4 w-full">
      {/* Floating Dark Shadow Pill Bar - Identical to Front Page Navbar */}
      <div className="relative rounded-2xl sm:rounded-full border border-white/[0.12] bg-[#080C17]/90 backdrop-blur-2xl px-4 py-2.5 sm:px-6 flex flex-wrap lg:flex-nowrap items-center justify-between gap-3 shadow-[0_20px_50px_rgba(0,0,0,0.95),0_0_30px_rgba(37,99,235,0.18),inset_0_1px_1px_rgba(255,255,255,0.15)] transition-all">
        {/* Subtle Ambient Beam */}
        <div className="absolute top-0 inset-x-12 h-[1px] bg-gradient-to-r from-transparent via-blue-400/50 to-transparent pointer-events-none" />

        {/* Brand & Home Navigation */}
        <div className="flex items-center gap-3">
          {onBackToHome && (
            <button
              onClick={onBackToHome}
              className="p-1.5 rounded-full bg-white/5 hover:bg-white/10 text-slate-300 hover:text-white transition cursor-pointer"
              title="Return to Front Page"
            >
              <ArrowLeft className="h-4 w-4" />
            </button>
          )}

          <div className="flex items-center gap-2.5">
            <div className="h-7 w-7 rounded-full bg-white flex items-center justify-center text-[#030712] shadow-md shadow-white/30">
              <Compass className="h-4 w-4 text-[#030712]" />
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-sm tracking-tight text-white font-outfit">
                  Neurolytix
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.2 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30">
                  Studio
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Sequential Workflow Tabs (Exact Match to Dark Luxury Capsule) */}
        <nav className="flex items-center gap-1 overflow-x-auto p-1 rounded-xl sm:rounded-full bg-white/5 border border-white/5 max-w-full">
          {steps.map((step) => {
            const Icon = step.icon;
            const isActive = activeTab === step.id;
            return (
              <button
                key={step.id}
                onClick={() => setActiveTab(step.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
                  isActive
                    ? 'bg-[#2563EB] text-white shadow-lg shadow-blue-600/40 ring-1 ring-blue-400/50'
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`}
              >
                <Icon className={`h-3.5 w-3.5 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{step.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right Status Indicators & Copilot Trigger */}
        <div className="flex items-center gap-2.5">
          {/* Active Dataset Pill */}
          {dataset && (
            <div className="hidden xl:flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-[11px] text-slate-300 font-mono">
              <span className="h-2 w-2 rounded-full bg-blue-400" />
              <span className="truncate max-w-[110px]">{dataset.filename}</span>
              <span className="text-slate-500">({dataset.rows}r)</span>
            </div>
          )}

          {/* Backend Status Badge */}
          <div
            className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold border font-mono ${
              backendHealth.online
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
            }`}
          >
            <span className={`h-2 w-2 rounded-full ${backendHealth.online ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
            <span className="hidden sm:inline">{backendHealth.online ? `API :8000 (${backendHealth.latencyMs}ms)` : 'API Offline'}</span>
            <span className="sm:hidden">{backendHealth.online ? 'Live' : 'Offline'}</span>
          </div>

          {/* Copilot Drawer CTA */}
          <button
            onClick={onOpenCopilot}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold shadow-[0_0_20px_rgba(37,99,235,0.4)] transition cursor-pointer hover:scale-105 active:scale-95"
          >
            <MessageSquareCode className="h-3.5 w-3.5" />
            <span className="hidden md:inline">AI Copilot</span>
          </button>
        </div>
      </div>
    </header>
  );
}
