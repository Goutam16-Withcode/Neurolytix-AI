'use client';

import React, { useState, useEffect } from 'react';
import { 
  BrainCircuit, 
  Sparkles, 
  CheckCircle2, 
  ArrowRight, 
  Sliders, 
  Layers, 
  Cpu, 
  ShieldCheck, 
  Wand2,
  FileCode2
} from 'lucide-react';
import { DatasetInfo } from '@/types';
import { api, DataScientistPlan } from '@/lib/api';

interface ScientistStudioProps {
  dataset: DatasetInfo;
  onNextStep: () => void;
}

export function ScientistStudio({ dataset, onNextStep }: ScientistStudioProps) {
  const [plan, setPlan] = useState<DataScientistPlan | null>(null);
  const [applied, setApplied] = useState(false);

  useEffect(() => {
    api.getDataScientistPlan().then((p) => setPlan(p));
  }, [dataset]);

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="p-6 rounded-2xl bg-[#090D1A]/90 border border-white/10 backdrop-blur-2xl relative overflow-hidden shadow-xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-blue-600/15 via-blue-700/10 to-transparent blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="px-2.5 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-[11px] font-bold text-blue-400">
                Phase 3: Autonomous Data Scientist
              </span>
              <span className="text-xs text-slate-400">•</span>
              <span className="text-xs text-slate-400 font-mono">Automated Feature Strategy</span>
            </div>
            <h1 className="text-2xl font-black font-outfit text-white tracking-tight">
              Dataset Intelligence & Modeling Strategy
            </h1>
            <p className="text-xs text-slate-400 max-w-2xl mt-1 leading-relaxed">
              The AI Data Scientist evaluates the EDA findings, detects distribution skews, and crafts an optimal preprocessing and architecture plan before model training.
            </p>
          </div>

          <button
            onClick={() => {
              setApplied(true);
              setTimeout(() => onNextStep(), 600);
            }}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold shadow-lg shadow-blue-600/40 transition cursor-pointer self-start md:self-auto hover:scale-105 active:scale-95"
          >
            <Wand2 className="h-4 w-4" />
            <span>{applied ? 'Strategy Applied ✓' : 'Apply Strategy & Design Model'}</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Plan Cards Grid */}
      {plan && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left 2 Cols: Formulated Pipeline */}
          <div className="lg:col-span-2 space-y-4">
            <h3 className="text-sm font-bold text-white font-outfit flex items-center gap-2">
              <BrainCircuit className="h-4 w-4 text-blue-400" />
              <span>Recommended Feature Pipeline Roadmap</span>
            </h3>

            <div className="space-y-3">
              {plan.pipelinePlan.map((step, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-xl bg-[#090D1A]/90 border border-white/10 hover:border-blue-500/30 transition flex items-start gap-3 shadow-lg"
                >
                  <span className="flex-shrink-0 h-6 w-6 rounded-lg bg-blue-500/20 text-blue-300 border border-blue-500/30 flex items-center justify-center font-bold text-xs">
                    {idx + 1}
                  </span>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-blue-400">{step.stage}</span>
                      <span className="text-[10px] text-emerald-400 font-semibold">✓ Automated</span>
                    </div>
                    <h4 className="text-xs font-bold text-white">{step.action}</h4>
                    <p className="text-xs text-slate-400 leading-relaxed">{step.reason}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right Col: Target & Problem Formulation */}
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white font-outfit flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-blue-400" />
              <span>Target Formulation</span>
            </h3>

            <div className="p-5 rounded-2xl bg-[#090D1A]/90 border border-white/10 space-y-4 shadow-xl">
              <div>
                <span className="text-[10px] font-bold text-slate-400 uppercase">Target Variable:</span>
                <p className="text-base font-extrabold text-blue-400 font-mono mt-0.5">{plan.recommendedTarget}</p>
              </div>

              <div>
                <span className="text-[10px] font-bold text-slate-400 uppercase">Problem Classification:</span>
                <p className="text-xs font-bold text-white mt-0.5">{plan.recommendedProblemType}</p>
              </div>

              <div className="p-3.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs space-y-1">
                <span className="font-bold text-blue-300">Dataset Dimensions:</span>
                <p className="text-slate-400 text-[11px] leading-relaxed">{plan.datasetSummary}</p>
              </div>

              <div className="pt-2 text-[11px] text-slate-500">
                Ready to train Tabular ML (CatBoost/LightGBM/XGBoost), Time Series, or NLP models in Phase 4.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
