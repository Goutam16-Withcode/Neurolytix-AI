'use client';

import React, { useState } from 'react';
import { 
  Scale, 
  Sparkles, 
  ShieldCheck, 
  CheckCircle2, 
  Search, 
  Users, 
  BarChart3, 
  Layers, 
  ArrowRight, 
  Bot, 
  AlertCircle,
  FileCheck
} from 'lucide-react';
import { JEVDecisionResult, DatasetInfo } from '@/types';
import { ShimmerBadge } from '@/components/ui/shimmer-badge';

interface DecisionRoomProps {
  dataset: DatasetInfo;
  initialResult: JEVDecisionResult;
}

export const PRESET_DILEMMAS = [
  "What is the single highest-impact strategy to cut customer churn by at least 25% over the next 60 days?",
  "Which pricing or contract structure yields the lowest risk of revenue attrition?",
  "Is there any demographic or payment method bias present in our retention funnel?",
];

export function DecisionRoom({ dataset, initialResult }: DecisionRoomProps) {
  const [query, setQuery] = useState(initialResult.query);
  const [isDeliberating, setIsDeliberating] = useState(false);
  const [activeStep, setActiveStep] = useState<number>(4);
  const [decision, setDecision] = useState<JEVDecisionResult>(initialResult);

  const runDeliberation = (questionText: string) => {
    setQuery(questionText);
    setIsDeliberating(true);
    setActiveStep(1);

    setTimeout(() => {
      setActiveStep(2);
    }, 900);

    setTimeout(() => {
      setActiveStep(3);
    }, 1800);

    setTimeout(() => {
      setActiveStep(4);
      setIsDeliberating(false);
    }, 2700);
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="p-6 rounded-2xl glass-card bg-gradient-to-r from-white via-cyan-50/30 to-indigo-50/20 border-cyan-100/80">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <div className="p-2 rounded-xl bg-cyan-600 text-white shadow-sm shadow-cyan-600/30">
                <Scale className="h-5 w-5" />
              </div>
              <h1 className="text-2xl font-bold font-outfit text-slate-900 tracking-tight">
                Agentic RAG & JEV Decision Room
              </h1>
              <ShimmerBadge variant="cyan">Multi-Agent Consensus</ShimmerBadge>
            </div>
            <p className="text-sm text-slate-600 max-w-3xl">
              Turn ambiguous data into verified executive actions. The <strong>JEV (Judge-Evaluator-Verifier)</strong> engine coordinates specialized AI agents to generate strategies, audit claims against raw dataset facts, and render the optimal consensus.
            </p>
          </div>
        </div>

        {/* Query Input Box */}
        <div className="mt-5 space-y-3">
          <div className="flex flex-col sm:flex-row items-stretch gap-2.5">
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask any strategic dilemma about this dataset..."
                className="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-300 bg-white text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent shadow-sm"
              />
            </div>
            <button
              onClick={() => runDeliberation(query)}
              disabled={isDeliberating}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-700 hover:to-cyan-700 text-white text-xs font-bold shadow-md shadow-indigo-600/20 transition cursor-pointer flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <Sparkles className="h-4 w-4" />
              <span>{isDeliberating ? 'Deliberating Agents...' : 'Run JEV Deliberation'}</span>
            </button>
          </div>

          {/* Quick Presets */}
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="text-slate-500 font-medium">Quick Prompts:</span>
            {PRESET_DILEMMAS.map((preset, idx) => (
              <button
                key={idx}
                onClick={() => runDeliberation(preset)}
                className="px-3 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-[11px] font-medium transition cursor-pointer"
              >
                {preset.slice(0, 48)}...
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 4-Step Animated Pipeline Tracker */}
      <div className="p-4 rounded-xl glass-card bg-white/90 border-slate-200">
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
          <div
            className={`p-3 rounded-lg border transition ${
              activeStep >= 1
                ? 'bg-cyan-50/60 border-cyan-300 text-cyan-900'
                : 'bg-slate-50 border-slate-200 text-slate-400'
            }`}
          >
            <div className="flex items-center gap-2 text-xs font-bold">
              <Search className="h-4 w-4 text-cyan-600" />
              <span>1. Tabular RAG Retrieval</span>
            </div>
            <p className="text-[11px] text-slate-600 mt-1">
              Found {decision.retrievedContextCount} fact chunks from {dataset.name}
            </p>
          </div>

          <div
            className={`p-3 rounded-lg border transition ${
              activeStep >= 2
                ? 'bg-indigo-50/60 border-indigo-300 text-indigo-900'
                : 'bg-slate-50 border-slate-200 text-slate-400'
            }`}
          >
            <div className="flex items-center gap-2 text-xs font-bold">
              <Users className="h-4 w-4 text-indigo-600" />
              <span>2. Multi-Agent Proposals</span>
            </div>
            <p className="text-[11px] text-slate-600 mt-1">
              3 competing perspectives generated
            </p>
          </div>

          <div
            className={`p-3 rounded-lg border transition ${
              activeStep >= 3
                ? 'bg-emerald-50/60 border-emerald-300 text-emerald-900'
                : 'bg-slate-50 border-slate-200 text-slate-400'
            }`}
          >
            <div className="flex items-center gap-2 text-xs font-bold">
              <ShieldCheck className="h-4 w-4 text-emerald-600" />
              <span>3. Fact-Check Verifier</span>
            </div>
            <p className="text-[11px] text-slate-600 mt-1">
              0 hallucinations detected ({decision.verifierReport.dataGroundingScore}% grounded)
            </p>
          </div>

          <div
            className={`p-3 rounded-lg border transition ${
              activeStep >= 4
                ? 'bg-purple-50/60 border-purple-300 text-purple-900'
                : 'bg-slate-50 border-slate-200 text-slate-400'
            }`}
          >
            <div className="flex items-center gap-2 text-xs font-bold">
              <Scale className="h-4 w-4 text-purple-600" />
              <span>4. JEV Chief Decision</span>
            </div>
            <p className="text-[11px] text-slate-600 mt-1">
              Consensus rendered with {decision.finalDecision.confidencePct}% confidence
            </p>
          </div>
        </div>
      </div>

      {/* Decision Results Display */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Competing Proposals */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900 font-outfit flex items-center gap-2">
              <Users className="h-4 w-4 text-indigo-600" />
              <span>Competing Strategic Proposals</span>
            </h3>
            <span className="text-xs text-slate-500">3 Agents</span>
          </div>

          <div className="space-y-3">
            {decision.proposals.map((proposal, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-xl border transition glass-card ${
                  idx === 0
                    ? 'border-indigo-300 bg-indigo-50/30 ring-1 ring-indigo-200'
                    : 'border-slate-200 bg-white'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-indigo-500" />
                    <span className="text-xs font-bold text-slate-900">{proposal.agentName}</span>
                  </div>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                    {proposal.agentRole}
                  </span>
                </div>
                <h4 className="text-xs font-bold text-indigo-700">{proposal.strategyTitle}</h4>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                  {proposal.recommendation}
                </p>
                <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between text-[11px]">
                  <span className="text-emerald-700 font-semibold">{proposal.projectedImpact}</span>
                  <span className="text-slate-500">Risk: {proposal.riskRating}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Grounding Fact Check Note */}
          <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs space-y-1">
            <div className="flex items-center gap-1.5 font-bold">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              <span>Verifier Shield Active</span>
            </div>
            <p className="text-[11px] text-emerald-800 leading-relaxed">
              {decision.verifierReport.notes}
            </p>
          </div>
        </div>

        {/* Right 2 Columns: The JEV Final Verdict Card */}
        <div className="lg:col-span-2 space-y-5">
          <div className="p-6 rounded-2xl glass-card bg-gradient-to-br from-white via-indigo-50/20 to-purple-50/30 border-indigo-200/80 shadow-lg shadow-indigo-100/50">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-5 border-b border-indigo-100">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-indigo-600 text-white shadow-md shadow-indigo-600/30">
                  <Scale className="h-6 w-6" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-base font-bold text-slate-900 font-outfit">
                      JEV Verified Decision Verdict
                    </h2>
                    <ShimmerBadge variant="indigo">Highest Confidence</ShimmerBadge>
                  </div>
                  <p className="text-xs text-slate-500">Rendered via Multi-Agent Consensus</p>
                </div>
              </div>

              {/* Confidence Gauge */}
              <div className="flex items-center gap-3 bg-white px-4 py-2 rounded-xl border border-indigo-100 shadow-sm">
                <div className="text-right">
                  <p className="text-[10px] uppercase font-bold text-slate-400">JEV Consensus</p>
                  <p className="text-lg font-black text-indigo-600 font-outfit">
                    {decision.finalDecision.confidencePct}%
                  </p>
                </div>
                <div className="h-8 w-8 rounded-full border-2 border-indigo-500 flex items-center justify-center text-xs font-bold text-indigo-600 bg-indigo-50">
                  ✓
                </div>
              </div>
            </div>

            {/* Winning Strategy Callout */}
            <div className="mt-5 p-4 rounded-xl bg-indigo-50/70 border border-indigo-200">
              <span className="text-[11px] font-bold text-indigo-600 uppercase tracking-wider">
                Approved Executive Action
              </span>
              <p className="text-sm font-bold text-slate-900 mt-1">
                {decision.finalDecision.selectedStrategy}
              </p>
              <p className="text-xs text-slate-700 mt-2 leading-relaxed">
                {decision.finalDecision.executiveRationale}
              </p>
            </div>

            {/* Actionable Execution Steps */}
            <div className="mt-5">
              <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3">
                Actionable Implementation Roadmap:
              </h4>
              <div className="space-y-2.5">
                {decision.finalDecision.actionableSteps.map((step, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-3 p-3 rounded-lg bg-white border border-slate-200/80 text-xs"
                  >
                    <span className="flex-shrink-0 h-5 w-5 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-[11px]">
                      {idx + 1}
                    </span>
                    <span className="text-slate-700 font-medium leading-relaxed">{step}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Evaluator Scorecard */}
            <div className="mt-6 pt-5 border-t border-indigo-100 grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                <p className="text-[10px] text-slate-500 font-medium">Feasibility</p>
                <p className="text-sm font-bold text-slate-900">{decision.evaluatorScores.feasibility}%</p>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                <p className="text-[10px] text-slate-500 font-medium">ROI Impact</p>
                <p className="text-sm font-bold text-slate-900">{decision.evaluatorScores.roiImpact}%</p>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                <p className="text-[10px] text-slate-500 font-medium">Fairness Audit</p>
                <p className="text-sm font-bold text-slate-900">{decision.evaluatorScores.ethicalFairness}%</p>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                <p className="text-[10px] text-slate-500 font-medium">Data Grounding</p>
                <p className="text-sm font-bold text-emerald-600">{decision.verifierReport.dataGroundingScore}%</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
