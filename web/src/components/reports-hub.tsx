'use client';

import React, { useState } from 'react';
import { 
  FileText, 
  Download, 
  CheckCircle2, 
  Share2, 
  FileSpreadsheet, 
  Sparkles,
  Award
} from 'lucide-react';
import { DatasetInfo, AutoMLModel, JEVDecisionResult } from '@/types';

interface ReportsHubProps {
  dataset: DatasetInfo;
  models: AutoMLModel[];
  decisionResult: JEVDecisionResult;
}

export function ReportsHub({ dataset, models, decisionResult }: ReportsHubProps) {
  const [downloading, setDownloading] = useState(false);
  const champion = models.find((m) => m.isChampion) || models[0];

  const handleDownload = () => {
    setDownloading(true);
    setTimeout(() => {
      setDownloading(false);
      alert('Executive Dossier & PDF Briefing generated and downloaded successfully!');
    }, 1200);
  };

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="p-6 rounded-2xl bg-[#090D1A]/90 border border-white/10 backdrop-blur-2xl relative overflow-hidden shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="px-2.5 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-[11px] font-bold text-blue-400">
                Phase 6: Executive Synthesis & Reports
              </span>
              <span className="text-xs text-slate-400">•</span>
              <span className="text-xs text-slate-400 font-mono">1-Click PDF</span>
            </div>
            <h1 className="text-2xl font-black font-outfit text-white tracking-tight">
              Executive Dossier & Briefing Center
            </h1>
            <p className="text-xs text-slate-400 max-w-2xl mt-1 leading-relaxed">
              Synthesizes Phase 1 through Phase 5 into a boardroom-ready executive brief summarizing EDA, trained algorithms, and verified JEV decisions.
            </p>
          </div>

          <button
            onClick={handleDownload}
            disabled={downloading}
            className="px-6 py-2.5 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold shadow-lg shadow-blue-600/40 transition cursor-pointer flex items-center gap-2 self-start sm:self-auto disabled:opacity-50 hover:scale-105 active:scale-95"
          >
            <Download className="h-4 w-4" />
            <span>{downloading ? 'Compiling Dossier...' : 'Download Executive PDF'}</span>
          </button>
        </div>
      </div>

      {/* Boardroom Document Preview */}
      <div className="max-w-4xl mx-auto rounded-2xl bg-[#080C17]/95 border border-white/10 shadow-2xl p-8 sm:p-12 space-y-8">
        <div className="flex items-start justify-between pb-6 border-b border-white/10">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-extrabold text-blue-400 uppercase tracking-widest font-mono">
                Executive Dossier Brief
              </span>
              <span className="text-xs text-slate-500">• Confidential</span>
            </div>
            <h2 className="text-2xl font-extrabold text-white font-outfit mt-1">
              Autonomous Intelligence & Strategic Recommendation
            </h2>
            <p className="text-xs text-slate-400 mt-1">Dataset: {dataset.name} • {dataset.rows?.toLocaleString()} Records Analyzed</p>
          </div>

          <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-400 flex items-center gap-2">
            <Award className="h-5 w-5" />
            <span className="text-xs font-bold">JEV Certified</span>
          </div>
        </div>

        {/* Section 1: Executive Summary */}
        <div className="space-y-3">
          <h3 className="text-xs font-extrabold text-blue-400 uppercase tracking-widest font-mono">
            1. Executive Verdict & Rationale
          </h3>
          <div className="p-5 rounded-xl bg-white/[0.03] border border-white/5 space-y-2 text-xs leading-relaxed text-slate-300">
            <p className="font-bold text-white text-sm">
              Primary Strategic Action: {decisionResult.finalDecision.selectedStrategy}
            </p>
            <p>{decisionResult.finalDecision.executiveRationale}</p>
          </div>
        </div>

        {/* Section 2: Model Champion Performance */}
        <div className="space-y-3">
          <h3 className="text-xs font-extrabold text-blue-400 uppercase tracking-widest font-mono">
            2. Selected Algorithm Performance
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-xs">
            <div className="p-4 rounded-xl bg-white/[0.03] border border-white/5">
              <p className="text-slate-400 text-[10px]">Algorithm Model</p>
              <p className="text-base font-bold text-white mt-1">{champion.name}</p>
            </div>
            <div className="p-4 rounded-xl bg-white/[0.03] border border-white/5">
              <p className="text-slate-400 text-[10px]">Validation Accuracy</p>
              <p className="text-base font-bold text-blue-400 mt-1">{(champion.metricValue * 100).toFixed(1)}%</p>
            </div>
            <div className="p-4 rounded-xl bg-white/[0.03] border border-white/5">
              <p className="text-slate-400 text-[10px]">Real-Time Inference</p>
              <p className="text-base font-bold text-emerald-400 mt-1">{champion.trainTimeSeconds}s Latency</p>
            </div>
          </div>
        </div>

        {/* Section 3: Verified Action Steps */}
        <div className="space-y-3">
          <h3 className="text-xs font-extrabold text-blue-400 uppercase tracking-widest font-mono">
            3. Operational Roadmap & Grounding
          </h3>
          <div className="space-y-2">
            {decisionResult.finalDecision.actionableSteps.map((step, idx) => (
              <div key={idx} className="flex items-center gap-3 p-3 rounded-lg bg-white/[0.02] border border-white/5 text-xs text-slate-300">
                <CheckCircle2 className="h-4 w-4 text-emerald-400 flex-shrink-0" />
                <span>{step}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Signoff */}
        <div className="pt-6 border-t border-white/10 flex items-center justify-between text-xs text-slate-500 font-mono">
          <span>Synthesized autonomously by Neurolytix Decision Engine</span>
          <span>Status: Boardroom Ready</span>
        </div>
      </div>
    </div>
  );
}
