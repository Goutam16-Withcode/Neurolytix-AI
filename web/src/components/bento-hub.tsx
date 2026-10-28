'use client';

import React from 'react';
import { 
  Sparkles, 
  Activity, 
  Trophy, 
  AlertTriangle, 
  Scale, 
  ArrowUpRight, 
  Zap, 
  CheckCircle, 
  FileSpreadsheet, 
  TrendingUp, 
  ShieldCheck, 
  Bot,
  Layers,
  ArrowRight
} from 'lucide-react';
import { DatasetInfo, AutoMLModel, JEVDecisionResult } from '@/types';
import { ShimmerBadge } from '@/components/ui/shimmer-badge';

interface BentoHubProps {
  dataset: DatasetInfo;
  models: AutoMLModel[];
  decisionResult: JEVDecisionResult;
  onNavigateTab: (tab: string) => void;
  onOpenCopilot: () => void;
}

export function BentoHub({
  dataset,
  models,
  decisionResult,
  onNavigateTab,
  onOpenCopilot,
}: BentoHubProps) {
  const championModel = models.find((m) => m.isChampion) || models[0];

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl glass-card bg-gradient-to-r from-white via-indigo-50/20 to-purple-50/15 border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xl">👋</span>
            <h1 className="text-2xl font-bold font-outfit text-slate-900 tracking-tight">
              AI Command & Decision Center
            </h1>
            <ShimmerBadge variant="emerald">Live & Synchronized</ShimmerBadge>
          </div>
          <p className="text-sm text-slate-600 max-w-2xl">
            Currently analyzing <span className="font-semibold text-slate-900">{dataset.name}</span>. 
            All automated cleaning, models, and multi-agent decision pipelines are ready.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => onNavigateTab('automl')}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 text-white text-xs font-semibold shadow-sm hover:bg-indigo-700 transition cursor-pointer"
          >
            <Zap className="h-4 w-4" />
            <span>1-Click AutoML</span>
          </button>
          <button
            onClick={() => onNavigateTab('jev')}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white border border-slate-300 text-slate-700 text-xs font-semibold hover:bg-slate-50 transition cursor-pointer shadow-2xs"
          >
            <Scale className="h-4 w-4 text-indigo-600" />
            <span>AI Decision Room</span>
          </button>
        </div>
      </div>

      {/* Professional Bento Grid Layout */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-5">
        {/* Bento 1: Dataset Intelligence & Health Score (Spans 2 cols) */}
        <div className="md:col-span-2 p-6 rounded-2xl glass-card border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-indigo-50 text-indigo-600 border border-indigo-100">
                <Activity className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900 font-outfit">Dataset Health & Readiness</h3>
                <p className="text-xs text-slate-500">Automated quality scan & integrity check</p>
              </div>
            </div>
            <div className="text-right">
              <span className="text-3xl font-extrabold text-indigo-600 font-outfit">
                {dataset.healthScore}%
              </span>
              <p className="text-[11px] font-semibold text-emerald-600">Excellent Condition</p>
            </div>
          </div>

          {/* Quick Metrics Strip */}
          <div className="grid grid-cols-3 gap-3 my-5 py-3 px-4 rounded-xl bg-slate-50 border border-slate-200/80">
            <div>
              <p className="text-[11px] font-medium text-slate-500">Total Records</p>
              <p className="text-base font-bold text-slate-900">{dataset.rows?.toLocaleString() || 0}</p>
            </div>
            <div>
              <p className="text-[11px] font-medium text-slate-500">Columns Analyzed</p>
              <p className="text-base font-bold text-slate-900">{dataset.columns} Features</p>
            </div>
            <div>
              <p className="text-[11px] font-medium text-slate-500">Missing Values</p>
              <p className="text-base font-bold text-slate-900">{dataset.missingCells} cells</p>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-slate-100">
            <div className="flex items-center gap-1.5 text-xs text-slate-500">
              <ShieldCheck className="h-4 w-4 text-emerald-500" />
              <span>Zero critical data leakage detected</span>
            </div>
            <button
              onClick={() => onNavigateTab('data')}
              className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800 cursor-pointer"
            >
              <span>Inspect Raw Data</span>
              <ArrowUpRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>

        {/* Bento 2: Model Champion Leaderboard Card */}
        <div className="p-6 rounded-2xl glass-card border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="p-2 rounded-xl bg-amber-50 text-amber-600 border border-amber-100">
                <Trophy className="h-5 w-5" />
              </div>
              <ShimmerBadge variant="amber" className="text-[10px]">
                Champion
              </ShimmerBadge>
            </div>
            <h3 className="text-sm font-bold text-slate-900 font-outfit">Top AI Model</h3>
            <p className="text-lg font-extrabold text-slate-800 mt-0.5">{championModel.name}</p>
            <div className="mt-2 flex items-baseline gap-1.5">
              <span className="text-2xl font-black text-indigo-600 font-outfit">
                {(championModel.metricValue * 100).toFixed(1)}%
              </span>
              <span className="text-xs font-medium text-slate-500">{championModel.metricName}</span>
            </div>
            <p className="text-xs text-slate-500 mt-2">
              Trained in {championModel.trainTimeSeconds}s • 5-fold cross validation
            </p>
          </div>

          <button
            onClick={() => onNavigateTab('automl')}
            className="mt-4 w-full py-2 px-3 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition flex items-center justify-center gap-1.5 cursor-pointer"
          >
            <span>View All Models</span>
            <ArrowUpRight className="h-3.5 w-3.5" />
          </button>
        </div>

        {/* Bento 3: Agentic RAG Decision Room Spotlight */}
        <div className="p-6 rounded-2xl glass-card bg-gradient-to-br from-white via-indigo-50/20 to-cyan-50/20 flex flex-col justify-between border border-cyan-100 shadow-xs">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="p-2 rounded-xl bg-cyan-50 text-cyan-600 border border-cyan-100">
                <Scale className="h-5 w-5" />
              </div>
              <ShimmerBadge variant="cyan" className="text-[10px]">
                JEV Verified
              </ShimmerBadge>
            </div>
            <h3 className="text-sm font-bold text-slate-900 font-outfit">Strategic Decision</h3>
            <p className="text-xs font-semibold text-slate-700 mt-1 line-clamp-2">
              &quot;{decisionResult.finalDecision.selectedStrategy}&quot;
            </p>
            <div className="mt-3 flex items-center gap-2">
              <div className="h-2 flex-1 rounded-full bg-slate-200 overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-cyan-500 to-indigo-600 rounded-full"
                  style={{ width: `${decisionResult.finalDecision.confidencePct}%` }}
                />
              </div>
              <span className="text-xs font-bold text-slate-800">
                {decisionResult.finalDecision.confidencePct}%
              </span>
            </div>
            <p className="text-[11px] text-slate-500 mt-1">Multi-agent verified consensus</p>
          </div>

          <button
            onClick={() => onNavigateTab('jev')}
            className="mt-4 w-full py-2 px-3 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-semibold transition flex items-center justify-center gap-1.5 cursor-pointer"
          >
            <span>Enter Decision Room</span>
            <ArrowUpRight className="h-3.5 w-3.5" />
          </button>
        </div>

        {/* Bento 4: Anomaly & Data Quality Radar (Spans 2 cols) */}
        <div className="md:col-span-2 p-6 rounded-2xl glass-card border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-rose-50 text-rose-600 border border-rose-100">
                  <AlertTriangle className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 font-outfit">
                    Anomaly & Error Spotter
                  </h3>
                  <p className="text-xs text-slate-500">Isolation Forest & LOF Scan</p>
                </div>
              </div>
              <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-rose-100 text-rose-800">
                {dataset.anomalyCount} Flagged Records
              </span>
            </div>

            <div className="space-y-2 mt-4">
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 text-xs">
                <span className="text-slate-600">High Outlier Monthly Spend (&gt; $180/mo)</span>
                <span className="font-semibold text-slate-800">11 instances</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 text-xs">
                <span className="text-slate-600">Frequent Support Escalations (4+ tickets)</span>
                <span className="font-semibold text-slate-800">5 instances</span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
            <span className="text-xs text-slate-500">Auto-clean can isolate or normalize these rows</span>
            <button
              onClick={() => onNavigateTab('data')}
              className="text-xs font-semibold text-rose-600 hover:text-rose-800 cursor-pointer"
            >
              Auto-Clean Anomalies →
            </button>
          </div>
        </div>

        {/* Bento 5: Interactive AI Copilot Callout (Spans 2 cols) */}
        <div className="md:col-span-2 p-6 rounded-2xl glass-card bg-gradient-to-r from-indigo-50/40 via-purple-50/25 to-white flex flex-col justify-between border border-indigo-200 shadow-xs">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="p-2 rounded-xl bg-indigo-600 text-white">
                <Bot className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900 font-outfit">Talk to Your Data in Plain English</h3>
                <p className="text-xs text-slate-500">Powered by Agentic RAG & Offline Embeddings</p>
              </div>
            </div>
            <p className="text-xs text-slate-600 mt-2">
              Ask natural language questions like &quot;Why are Month-to-Month customers leaving?&quot; or &quot;Show me the average spend of churned vs loyal users.&quot;
            </p>
          </div>

          <div className="mt-4 flex items-center gap-2">
            <button
              onClick={onOpenCopilot}
              className="flex-1 py-2.5 px-4 rounded-xl bg-white border border-indigo-200 text-indigo-700 text-xs font-semibold hover:bg-indigo-50/50 transition flex items-center justify-between cursor-pointer shadow-xs"
            >
              <span>Click to ask a question...</span>
              <Sparkles className="h-4 w-4 text-indigo-500" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
