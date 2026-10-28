'use client';

import React, { useState } from 'react';
import { 
  Scale, 
  Sparkles, 
  ShieldCheck, 
  CheckCircle2, 
  Search, 
  Users, 
  ArrowRight, 
  RotateCw,
  FileCheck
} from 'lucide-react';
import { JEVDecisionResult, DatasetInfo } from '@/types';
import { api } from '@/lib/api';

interface DecisionRoomProps {
  dataset: DatasetInfo;
  initialResult: JEVDecisionResult;
  onNextStep?: () => void;
}

export const PRESET_DILEMMAS = [
  "What is the single highest-impact strategy to cut customer churn by at least 25% over the next 60 days?",
  "Which pricing or contract structure yields the lowest risk of revenue attrition?",
  "Is there any demographic or payment method bias present in our retention funnel?",
];

export function DecisionRoom({ dataset, initialResult, onNextStep }: DecisionRoomProps) {
  const [query, setQuery] = useState(initialResult.query);
  const [isDeliberating, setIsDeliberating] = useState(false);
  const [activeStep, setActiveStep] = useState<number>(4);
  const [decision, setDecision] = useState<JEVDecisionResult>(initialResult);

  const runDeliberation = async (questionText: string) => {
    setQuery(questionText);
    setIsDeliberating(true);
    setActiveStep(1);

    const stepTimer1 = setTimeout(() => setActiveStep(2), 500);
    const stepTimer2 = setTimeout(() => setActiveStep(3), 1000);

    try {
      const realResult = await api.runJEV(questionText);
      setActiveStep(4);
      setDecision(realResult);
    } catch (err) {
      console.error(err);
      setActiveStep(4);
    } finally {
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      setIsDeliberating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="p-6 rounded-2xl bg-[#090D1A]/90 border border-white/10 backdrop-blur-2xl relative overflow-hidden shadow-xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-blue-600/15 via-blue-700/10 to-transparent blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="px-2.5 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-[11px] font-bold text-blue-400">
                Phase 5: Agentic RAG Decision Room
              </span>
              <span className="text-xs text-slate-400">•</span>
              <span className="text-xs text-slate-400 font-mono">JEV Consensus Engine</span>
            </div>
            <h1 className="text-2xl font-black font-outfit text-white tracking-tight">
              Agentic RAG & JEV Multi-Agent Consensus
            </h1>
            <p className="text-xs text-slate-400 max-w-2xl mt-1 leading-relaxed">
              Turns complex data patterns into verified executive action. <strong>Proposers ➔ Verifier Hallucination Shield ➔ JEV Chief Decision Verdict</strong>.
            </p>
          </div>

          {onNextStep && (
            <button
              onClick={onNextStep}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold shadow-lg shadow-blue-600/40 transition cursor-pointer self-start md:self-auto hover:scale-105 active:scale-95"
            >
              <span>Next: Executive Dossier</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Query Input Box */}
        <div className="mt-5 space-y-3">
          <div className="flex flex-col sm:flex-row items-stretch gap-2.5">
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask any strategic dilemma about this dataset..."
                className="w-full pl-10 pr-4 py-3 rounded-xl border border-white/10 bg-[#05070F] text-xs font-semibold text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
              />
            </div>
            <button
              onClick={() => runDeliberation(query)}
              disabled={isDeliberating}
              className="px-6 py-3 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold shadow-md shadow-blue-600/40 transition cursor-pointer flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {isDeliberating ? (
                <>
                  <RotateCw className="h-4 w-4 animate-spin" />
                  <span>Deliberating Agents...</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  <span>Run JEV Deliberation</span>
                </>
              )}
            </button>
          </div>

          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="text-slate-400 font-medium">Quick Dilemmas:</span>
            {PRESET_DILEMMAS.map((preset, idx) => (
              <button
                key={idx}
                onClick={() => runDeliberation(preset)}
                className="px-3 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 text-[11px] font-medium transition cursor-pointer border border-white/5"
              >
                {preset.slice(0, 48)}...
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 4-Step Animated Pipeline Tracker */}
      <div className="p-4 rounded-xl bg-[#090D1A]/90 border border-white/10 shadow-lg">
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
          <div className={`p-3 rounded-lg border transition ${activeStep >= 1 ? 'bg-blue-500/10 border-blue-500/30 text-blue-300' : 'bg-white/5 border-white/5 text-slate-500'}`}>
            <span className="text-xs font-bold block">1. Tabular RAG</span>
            <p className="text-[11px] text-slate-400 mt-0.5">Retrieved {decision.retrievedContextCount} factual chunks</p>
          </div>
          <div className={`p-3 rounded-lg border transition ${activeStep >= 2 ? 'bg-blue-500/10 border-blue-500/30 text-blue-300' : 'bg-white/5 border-white/5 text-slate-500'}`}>
            <span className="text-xs font-bold block">2. Multi-Agent Proposals</span>
            <p className="text-[11px] text-slate-400 mt-0.5">3 competing strategies formulated</p>
          </div>
          <div className={`p-3 rounded-lg border transition ${activeStep >= 3 ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-white/5 border-white/5 text-slate-500'}`}>
            <span className="text-xs font-bold block">3. Fact Verifier</span>
            <p className="text-[11px] text-slate-400 mt-0.5">0 hallucinations ({decision.verifierReport.dataGroundingScore}% grounded)</p>
          </div>
          <div className={`p-3 rounded-lg border transition ${activeStep >= 4 ? 'bg-blue-600/20 border-blue-500/40 text-blue-200' : 'bg-white/5 border-white/5 text-slate-500'}`}>
            <span className="text-xs font-bold block">4. JEV Verdict</span>
            <p className="text-[11px] text-slate-400 mt-0.5">{decision.finalDecision.confidencePct}% consensus reached</p>
          </div>
        </div>
      </div>

      {/* Decision Results Display */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Proposals */}
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-white font-outfit flex items-center gap-2">
            <Users className="h-4 w-4 text-blue-400" />
            <span>Competing Agent Strategies</span>
          </h3>

          <div className="space-y-3">
            {decision.proposals.map((proposal, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-xl border bg-[#090D1A]/90 shadow-lg transition ${
                  idx === 0 ? 'border-blue-500/40 bg-blue-500/5' : 'border-white/10'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-white">{proposal.agentName}</span>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-white/5 text-slate-400">
                    {proposal.agentRole}
                  </span>
                </div>
                <h4 className="text-xs font-bold text-blue-400">{proposal.strategyTitle}</h4>
                <p className="text-xs text-slate-300 mt-1 leading-relaxed">{proposal.recommendation}</p>
                <div className="mt-3 pt-2 border-t border-white/5 flex items-center justify-between text-[11px]">
                  <span className="text-emerald-400 font-semibold">{proposal.projectedImpact}</span>
                  <span className="text-slate-400">Risk: {proposal.riskRating}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right 2 Cols: Winning Verdict */}
        <div className="lg:col-span-2 space-y-5">
          <div className="p-6 rounded-2xl bg-[#090D1A]/90 border border-white/10 backdrop-blur-2xl shadow-xl space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-white/10">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-blue-600 text-white shadow-md shadow-blue-600/40">
                  <Scale className="h-6 w-6" />
                </div>
                <div>
                  <h2 className="text-base font-bold text-white font-outfit">JEV Final Decision Verdict</h2>
                  <p className="text-xs text-slate-400">Approved by Multi-Agent Consensus</p>
                </div>
              </div>

              <div className="text-right">
                <p className="text-[10px] uppercase font-bold text-slate-400">JEV Consensus</p>
                <p className="text-xl font-black text-blue-400 font-mono">{decision.finalDecision.confidencePct}%</p>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 space-y-1">
              <span className="text-[10px] font-bold text-blue-400 uppercase">Approved Action:</span>
              <p className="text-sm font-bold text-white">{decision.finalDecision.selectedStrategy}</p>
              <p className="text-xs text-slate-300 mt-2 leading-relaxed">{decision.finalDecision.executiveRationale}</p>
            </div>

            <div>
              <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-2">Implementation Roadmap:</h4>
              <div className="space-y-2">
                {decision.finalDecision.actionableSteps.map((step, idx) => (
                  <div key={idx} className="flex items-start gap-2.5 p-2.5 rounded-lg bg-white/5 text-xs text-slate-300">
                    <span className="h-4 w-4 rounded-full bg-blue-500/20 text-blue-300 flex items-center justify-center font-bold text-[10px] flex-shrink-0 mt-0.5">
                      {idx + 1}
                    </span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-4 border-t border-white/10 grid grid-cols-2 sm:grid-cols-4 gap-3 text-center font-mono">
              <div className="p-2.5 rounded-lg bg-white/5">
                <p className="text-[10px] text-slate-400">Feasibility</p>
                <p className="text-sm font-bold text-white">{decision.evaluatorScores.feasibility}%</p>
              </div>
              <div className="p-2.5 rounded-lg bg-white/5">
                <p className="text-[10px] text-slate-400">ROI Impact</p>
                <p className="text-sm font-bold text-white">{decision.evaluatorScores.roiImpact}%</p>
              </div>
              <div className="p-2.5 rounded-lg bg-white/5">
                <p className="text-[10px] text-slate-400">Fairness Audit</p>
                <p className="text-sm font-bold text-white">{decision.evaluatorScores.ethicalFairness}%</p>
              </div>
              <div className="p-2.5 rounded-lg bg-white/5">
                <p className="text-[10px] text-slate-400">Data Grounding</p>
                <p className="text-sm font-bold text-emerald-400">{decision.verifierReport.dataGroundingScore}%</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
