'use client';

import React, { useState } from 'react';
import { useAuth } from '@/context/auth-context';
import { NavbarDarkShadow } from '@/components/ui/navbar-dark-shadow';
import { StatsWithGradient } from '@/components/ui/stats-with-gradient';
import { SimpleFooterWithFourGrids } from '@/components/ui/simple-footer-with-four-grids';
import { 
  Compass, 
  ArrowUp, 
  Sparkles, 
  Database, 
  BarChart3, 
  Cpu, 
  Scale, 
  ArrowRight, 
  Check, 
  ShieldCheck, 
  Layers, 
  Play, 
  Brain, 
  Rocket, 
  CheckCircle2, 
  FileText,
  Activity,
  Zap,
  TrendingUp,
  AlertCircle,
  Table,
  Sliders,
  ChevronRight
} from 'lucide-react';

interface FrontPageProps {
  onLaunchStudio: () => void;
  onTrySample: (sampleKey?: string) => void;
}

export function FrontPage({ onLaunchStudio, onTrySample }: FrontPageProps) {
  const { user, openAuthModal, logout } = useAuth();
  const [promptInput, setPromptInput] = useState('');
  const [activePill, setActivePill] = useState<'eda' | 'automl' | 'jev'>('eda');

  const handlePromptSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onLaunchStudio();
  };

  const sampleDatasets = [
    {
      id: 'ecommerce-churn',
      name: 'E-Commerce Churn',
      type: 'Tabular ML',
      rows: '700 rows',
      desc: 'Predict customer churn risk from activity, tenure & spend.',
      color: 'from-blue-500/20 to-cyan-500/10',
      border: 'border-blue-500/30'
    },
    {
      id: 'saas-revenue',
      name: 'SaaS Monthly ARR',
      type: 'Time-Series',
      rows: '24 months',
      desc: 'Forecast monthly recurring revenue trends using Prophet.',
      color: 'from-indigo-500/20 to-purple-500/10',
      border: 'border-indigo-500/30'
    },
    {
      id: 'support-tickets',
      name: 'Customer Support NLP',
      type: 'NLP Text',
      rows: '1,200 tickets',
      desc: 'Categorize sentiment, urgency and root causes automatically.',
      color: 'from-emerald-500/20 to-teal-500/10',
      border: 'border-emerald-500/30'
    }
  ];

  const platformFeatureStats = [
    {
      value: "< 10ms",
      label: "Live Inference",
      description: "Sub-10ms real-time REST prediction engine deployed on FastAPI with live interactive parameter simulator."
    },
    {
      value: "94.8%",
      label: "Tournament Champion",
      description: "CatBoost & LightGBM multi-model validation accuracy achieved on Tabular benchmarks (CV removed)."
    },
    {
      value: "100%",
      label: "Grounded Citations",
      description: "Protected by JEV multi-agent factual verifier shield. Zero hallucinations allowed into executive decisions."
    },
    {
      value: "6+ Models",
      label: "Multi-Data Algorithms",
      description: "CatBoost, LightGBM, XGBoost, Prophet Time-Series & NLP Text Classifiers tailored by feature data types."
    }
  ];

  return (
    <div className="min-h-screen bg-[#030712] text-white relative overflow-hidden flex flex-col font-sans selection:bg-blue-600/30 selection:text-blue-200">
      {/* Signature Celestial Sapphire Diffuse Mesh Background (Exact Image Match) */}
      <div className="pointer-events-none absolute -top-40 right-0 w-[850px] h-[850px] bg-gradient-to-br from-blue-600/25 via-blue-700/15 to-transparent blur-[140px] rounded-full" />
      <div className="pointer-events-none absolute top-1/3 -left-40 w-[650px] h-[650px] bg-gradient-to-tr from-blue-700/20 via-indigo-600/15 to-transparent blur-[160px] rounded-full" />
      <div className="pointer-events-none absolute bottom-0 right-1/4 w-[800px] h-[700px] bg-gradient-to-t from-blue-600/30 via-indigo-700/20 to-transparent blur-[150px] rounded-full" />

      {/* Floating Aceternity Dark Shadow Navbar */}
      <NavbarDarkShadow
        user={user}
        onLaunchStudio={onLaunchStudio}
        onOpenAuth={(mode) => openAuthModal(mode || 'login')}
        onLogout={logout}
      />

      {/* Hero Section */}
      <main className="flex-1 relative z-10 flex flex-col items-center justify-center text-center px-4 pt-32 sm:pt-36 pb-12 max-w-5xl mx-auto">
        {/* Subtle Top Badge */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/25 text-blue-300 text-xs font-semibold backdrop-blur-md mb-6 animate-in fade-in slide-in-from-top-2">
          <Sparkles className="h-3.5 w-3.5 text-blue-400" />
          <span>Autonomous Data Science Studio v2.0 • Live FastAPI Engine</span>
        </div>

        {/* Main Hero Headline (Matches Screenshot) */}
        <h1 className="text-5xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-white font-outfit leading-[1.08] max-w-4xl">
          Plan data pipelines that feel like you planned them
        </h1>

        {/* Subtitle */}
        <p className="mt-6 text-sm sm:text-base text-slate-300 max-w-2xl mx-auto leading-relaxed">
          Tell Neurolytix what you want to predict and it drafts automated EDA, trains multi-algorithm models around your dataset, and renders verified JEV decisions. No spreadsheets. No forty open tabs.
        </p>

        {/* Switcher Pill */}
        <div className="mt-8 inline-flex items-center p-1 rounded-full bg-white/10 border border-white/10 backdrop-blur-md">
          <button
            onClick={() => setActivePill('eda')}
            className={`flex items-center gap-1.5 px-4 py-1.5 rounded-full text-xs font-semibold transition cursor-pointer ${
              activePill === 'eda'
                ? 'bg-white text-slate-900 shadow-md font-bold'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <BarChart3 className="h-3.5 w-3.5" />
            <span>Automated EDA</span>
          </button>
          <button
            onClick={() => setActivePill('automl')}
            className={`flex items-center gap-1.5 px-4 py-1.5 rounded-full text-xs font-semibold transition cursor-pointer ${
              activePill === 'automl'
                ? 'bg-white text-slate-900 shadow-md font-bold'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <Cpu className="h-3.5 w-3.5" />
            <span>AutoML & Deploy</span>
          </button>
          <button
            onClick={() => setActivePill('jev')}
            className={`flex items-center gap-1.5 px-4 py-1.5 rounded-full text-xs font-semibold transition cursor-pointer ${
              activePill === 'jev'
                ? 'bg-white text-slate-900 shadow-md font-bold'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <Scale className="h-3.5 w-3.5" />
            <span>JEV Decisions</span>
          </button>
        </div>

        {/* Signature Prompt Search Pill (Exact Visual Match to Screenshot) */}
        <form
          onSubmit={handlePromptSubmit}
          className="mt-6 w-full max-w-2xl bg-[#090D1A]/95 border border-white/15 rounded-full p-2 pl-6 flex items-center justify-between shadow-[0_20px_50px_rgba(0,0,0,0.9),0_0_30px_rgba(37,99,235,0.25)] backdrop-blur-2xl group hover:border-blue-500/50 transition duration-300"
        >
          <input
            type="text"
            value={promptInput}
            onChange={(e) => setPromptInput(e.target.value)}
            placeholder={
              activePill === 'eda'
                ? "Upload dataset, show histograms, correlations & outlier detection..."
                : activePill === 'automl'
                ? "Train CatBoost vs LightGBM on target column with real-time deployment..."
                : "What is the #1 recommended business strategy based on JEV consensus?"
            }
            className="flex-1 bg-transparent text-sm text-white placeholder-slate-400 focus:outline-none"
          />
          <button
            type="submit"
            className="h-10 w-10 rounded-full bg-[#2563EB] hover:bg-[#1D4ED8] text-white flex items-center justify-center transition cursor-pointer shadow-md shadow-blue-600/50 flex-shrink-0 hover:scale-105 active:scale-95"
            title="Launch Studio"
          >
            <ArrowUp className="h-5 w-5" />
          </button>
        </form>

        {/* Instant Demo Link */}
        <div className="mt-4 flex items-center justify-center gap-3">
          <button
            onClick={() => onTrySample('ecommerce-churn')}
            className="inline-flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 font-semibold cursor-pointer transition hover:underline"
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>Try it with your next dataset (Instant Demo) →</span>
          </button>
        </div>

        {/* 1-Click Interactive Benchmark Datasets Selector */}
        <div className="mt-10 w-full text-left">
          <div className="flex items-center justify-between mb-3 px-1">
            <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider font-semibold">
              Or Launch Directly With Pre-Loaded Benchmarks:
            </span>
            <span className="text-[11px] text-blue-400 font-semibold hidden sm:inline">
              1-Click Instant Ingestion
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {sampleDatasets.map((ds) => (
              <div
                key={ds.id}
                onClick={() => onTrySample(ds.id)}
                className={`p-4 rounded-2xl bg-[#090D18]/90 border ${ds.border} hover:bg-white/[0.08] transition-all cursor-pointer group shadow-xl backdrop-blur-xl relative overflow-hidden`}
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${ds.color} opacity-40 pointer-events-none`} />
                <div className="relative z-10 flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-white group-hover:text-blue-300 transition">
                    {ds.name}
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/10 text-slate-300">
                    {ds.type}
                  </span>
                </div>
                <p className="relative z-10 text-[11px] text-slate-400 leading-snug">
                  {ds.desc}
                </p>
                <div className="relative z-10 mt-3 pt-2 border-t border-white/10 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                  <span>{ds.rows}</span>
                  <span className="text-blue-400 font-bold group-hover:translate-x-1 transition flex items-center gap-1">
                    Open Studio <ChevronRight className="h-3 w-3" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Interactive Live Studio Preview Mockup */}
        <div className="mt-14 w-full rounded-3xl bg-[#080C17]/90 border border-white/15 p-5 shadow-[0_25px_60px_rgba(0,0,0,0.95),0_0_30px_rgba(37,99,235,0.2)] backdrop-blur-2xl text-left relative overflow-hidden">
          {/* Top Mock Window Bar */}
          <div className="flex items-center justify-between pb-4 border-b border-white/10">
            <div className="flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-rose-500/80" />
              <div className="h-3 w-3 rounded-full bg-amber-500/80" />
              <div className="h-3 w-3 rounded-full bg-emerald-500/80" />
              <span className="ml-2 text-xs font-mono text-slate-400 font-semibold">
                Neurolytix Autonomous Studio • customer_churn.csv (700 rows)
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-mono font-bold flex items-center gap-1">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Live Engine Active
              </span>
              <button
                onClick={onLaunchStudio}
                className="px-3 py-1 rounded-full bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold shadow-md shadow-blue-600/30 cursor-pointer transition flex items-center gap-1"
              >
                <span>Launch Live</span>
                <ArrowRight className="h-3 w-3" />
              </button>
            </div>
          </div>

          {/* 3-Column Studio Showcase */}
          <div className="mt-4 grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Column 1: Dynamic EDA Preview */}
            <div className="p-4 rounded-xl bg-white/[0.03] border border-white/10 space-y-3">
              <div className="flex items-center justify-between text-xs font-bold text-white">
                <div className="flex items-center gap-1.5 text-blue-400">
                  <BarChart3 className="h-4 w-4" />
                  <span>Dynamic Visual EDA</span>
                </div>
                <span className="text-[10px] font-mono text-slate-400">Numeric KDE</span>
              </div>
              <div className="h-24 w-full flex items-end justify-between gap-1.5 px-2 pt-4 bg-[#030712]/60 rounded-lg border border-white/5">
                {[30, 45, 60, 85, 95, 75, 55, 40, 25, 15].map((val, i) => (
                  <div key={i} className="flex-1 flex flex-col items-center gap-1">
                    <div 
                      className="w-full bg-gradient-to-t from-blue-600 to-cyan-400 rounded-t-sm hover:brightness-125 transition"
                      style={{ height: `${val}%` }}
                    />
                  </div>
                ))}
              </div>
              <p className="text-[11px] text-slate-300">
                Outlier scan: <strong>0 critical anomalies</strong>. Normal distribution confirmed across numeric features.
              </p>
            </div>

            {/* Column 2: AutoML Tournament */}
            <div className="p-4 rounded-xl bg-white/[0.03] border border-white/10 space-y-3">
              <div className="flex items-center justify-between text-xs font-bold text-white">
                <div className="flex items-center gap-1.5 text-indigo-400">
                  <Rocket className="h-4 w-4" />
                  <span>AutoML Leaderboard</span>
                </div>
                <span className="text-[10px] font-mono text-emerald-400 font-bold">Sub-10ms</span>
              </div>
              <div className="space-y-1.5 font-mono text-xs">
                <div className="p-2 rounded-lg bg-blue-600/15 border border-blue-500/30 flex items-center justify-between text-white">
                  <span className="font-bold">🥇 CatBoost Classifier</span>
                  <span className="text-emerald-400 font-bold">94.8% ROC-AUC</span>
                </div>
                <div className="p-2 rounded-lg bg-white/5 border border-white/5 flex items-center justify-between text-slate-400">
                  <span>🥈 LightGBM</span>
                  <span className="text-slate-300">93.1% ROC-AUC</span>
                </div>
                <div className="p-2 rounded-lg bg-white/5 border border-white/5 flex items-center justify-between text-slate-400">
                  <span>🥉 Prophet Time-Series</span>
                  <span className="text-slate-300">9.4% MAPE</span>
                </div>
              </div>
            </div>

            {/* Column 3: JEV Decision Room */}
            <div className="p-4 rounded-xl bg-white/[0.03] border border-white/10 space-y-3">
              <div className="flex items-center justify-between text-xs font-bold text-white">
                <div className="flex items-center gap-1.5 text-cyan-400">
                  <Scale className="h-4 w-4" />
                  <span>JEV Decision Consensus</span>
                </div>
                <span className="text-[10px] font-mono text-cyan-300 font-bold">Consensus 94%</span>
              </div>
              <div className="space-y-2 text-xs">
                <div className="p-2 rounded-lg bg-white/5 border border-white/5 text-[11px] text-slate-300">
                  <span className="font-bold text-white">Strategic Verdict:</span> Prioritize proactive retention for accounts in months 2-6 with high ticket volume.
                </div>
                <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-1">
                  <span className="flex items-center gap-1 text-emerald-400">
                    <ShieldCheck className="h-3 w-3" /> Hallucination-Free
                  </span>
                  <span className="text-blue-400 font-bold">JEV Judge Approved</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Feature Highlights Grid */}
        <div id="pipeline" className="mt-20 w-full grid grid-cols-1 md:grid-cols-3 gap-5 text-left">
          <div id="eda" className="p-6 rounded-2xl bg-[#090D18]/90 border border-white/10 backdrop-blur-md space-y-2.5 hover:border-blue-500/30 transition shadow-xl">
            <div className="h-8 w-8 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30 flex items-center justify-center">
              <BarChart3 className="h-4 w-4" />
            </div>
            <h3 className="text-sm font-bold text-white font-outfit">Dynamic Visual EDA</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Auto-infers types: Histograms, Box plots, Correlation heatmaps, Time-Series trends, and NLP keyword frequencies. Computer Vision (CV) completely removed for speed and clarity.
            </p>
          </div>

          <div id="automl" className="p-6 rounded-2xl bg-[#090D18]/90 border border-white/10 backdrop-blur-md space-y-2.5 hover:border-blue-500/30 transition shadow-xl">
            <div className="h-8 w-8 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center">
              <Rocket className="h-4 w-4" />
            </div>
            <h3 className="text-sm font-bold text-white font-outfit">Multi-Model & Deployment</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Train CatBoost, LightGBM, XGBoost, Prophet, and NLP classifiers. Deploy with sub-10ms real-time inference simulators and ready cURL endpoints.
            </p>
          </div>

          <div id="jev" className="p-6 rounded-2xl bg-[#090D18]/90 border border-white/10 backdrop-blur-md space-y-2.5 hover:border-blue-500/30 transition shadow-xl">
            <div className="h-8 w-8 rounded-lg bg-cyan-600/20 text-cyan-400 border border-cyan-500/30 flex items-center justify-center">
              <Scale className="h-4 w-4" />
            </div>
            <h3 className="text-sm font-bold text-white font-outfit">Agentic RAG & JEV Engine</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Multi-agent deliberation: Proposers ➔ Verifier Hallucination Shield ➔ JEV Chief Decision Verdict with grounded citations.
            </p>
          </div>
        </div>
      </main>

      {/* Aceternity Stats With Gradient Section (Matches Image 2) */}
      <StatsWithGradient
        title="Engineered for autonomous intelligence at scale"
        subtitle="We replaced brittle notebooks and manual pipelines with verified autonomous agents, real-time ML deployment, and zero-hallucination consensus."
        stats={platformFeatureStats}
      />

      {/* Enterprise Callout Banner */}
      <div id="pricing" className="max-w-5xl mx-auto px-4 mb-20 w-full relative z-10">
        <div className="rounded-3xl bg-gradient-to-r from-blue-900/25 via-indigo-950/40 to-blue-900/25 border border-white/10 p-8 text-center backdrop-blur-xl shadow-2xl">
          <h2 className="text-xl sm:text-2xl font-bold font-outfit text-white">
            Built for Real-World Data Scientists & Decision Makers
          </h2>
          <p className="text-xs text-slate-300 mt-2 max-w-lg mx-auto leading-relaxed">
            Zero configuration setup. Connect CSV, TSV, or JSON data streams and get autonomous end-to-end intelligence in minutes.
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-4">
            <button
              onClick={() => onTrySample('ecommerce-churn')}
              className="px-6 py-2.5 rounded-full bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-lg shadow-blue-600/50 transition cursor-pointer hover:scale-105 active:scale-95"
            >
              Launch Instant Demo
            </button>
            <button
              onClick={onLaunchStudio}
              className="px-6 py-2.5 rounded-full bg-white/10 hover:bg-white/15 text-white font-semibold text-xs border border-white/15 transition cursor-pointer"
            >
              Enter Dashboard
            </button>
          </div>
        </div>
      </div>

      {/* Aceternity Simple Footer with Four Grids (Matches Image 1, replaces old footer) */}
      <SimpleFooterWithFourGrids
        onOpenAuth={(mode) => openAuthModal(mode || 'login')}
        onLaunchStudio={onLaunchStudio}
      />
    </div>
  );
}
