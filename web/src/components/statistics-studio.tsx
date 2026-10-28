'use client';

import React, { useState, useEffect } from 'react';
import { 
  FlaskConical, 
  CheckCircle2, 
  AlertCircle, 
  RotateCw, 
  ArrowRight,
  TrendingUp,
  Percent,
  Sparkles
} from 'lucide-react';
import { DatasetInfo } from '@/types';
import { api, HypothesisTestResult } from '@/lib/api';
import { ShimmerBadge } from '@/components/ui/shimmer-badge';

interface StatisticsStudioProps {
  dataset: DatasetInfo;
  onNextStep?: () => void;
}

export function StatisticsStudio({ dataset, onNextStep }: StatisticsStudioProps) {
  const [selectedFeature, setSelectedFeature] = useState<string>('monthly_spend');
  const [selectedTarget, setSelectedTarget] = useState<string>('churned');
  const [testResult, setTestResult] = useState<HypothesisTestResult | null>(null);
  const [loading, setLoading] = useState(false);

  const runTest = async (feat?: string, targ?: string) => {
    const f = feat || selectedFeature;
    const t = targ || selectedTarget;
    setLoading(true);
    try {
      const res = await api.runHypothesisTest(f, t);
      setTestResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runTest();
  }, [dataset]);

  const numericCols = dataset.columnList?.filter((c) => c.type === 'numeric') || [];
  const catCols = dataset.columnList?.filter((c) => c.type === 'categorical') || [];

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="p-6 rounded-2xl glass-card bg-gradient-to-r from-white via-indigo-50/20 to-purple-50/20 border border-slate-200 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <div className="p-2 rounded-xl bg-purple-600 text-white shadow-xs">
                <FlaskConical className="h-5 w-5" />
              </div>
              <h1 className="text-2xl font-bold font-outfit text-slate-900 tracking-tight">
                Statistical & Hypothesis Testing Framework
              </h1>
              <ShimmerBadge variant="purple">P-Value Significance</ShimmerBadge>
            </div>
            <p className="text-sm text-slate-600 max-w-2xl">
              Conduct rigorous two-sample Welch&apos;s T-Tests and ANOVA variance checks to confirm whether observed differences in your data are statistically significant.
            </p>
          </div>

          {onNextStep && (
            <button
              onClick={onNextStep}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-sm transition cursor-pointer self-start md:self-auto"
            >
              <span>Proceed to AutoML Tournament</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Feature & Target Controls */}
        <div className="mt-5 grid grid-cols-1 sm:grid-cols-3 gap-3 p-4 rounded-xl bg-slate-50 border border-slate-200">
          <div>
            <label className="text-[11px] font-bold text-slate-600 block mb-1">Continuous Feature (X)</label>
            <select
              value={selectedFeature}
              onChange={(e) => {
                setSelectedFeature(e.target.value);
                runTest(e.target.value, selectedTarget);
              }}
              className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white text-xs font-semibold text-slate-800 shadow-xs focus:outline-none"
            >
              {numericCols.map((c) => (
                <option key={c.name} value={c.name}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-[11px] font-bold text-slate-600 block mb-1">Grouping Target (Y)</label>
            <select
              value={selectedTarget}
              onChange={(e) => {
                setSelectedTarget(e.target.value);
                runTest(selectedFeature, e.target.value);
              }}
              className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white text-xs font-semibold text-slate-800 shadow-xs focus:outline-none"
            >
              {catCols.map((c) => (
                <option key={c.name} value={c.name}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={() => runTest()}
              disabled={loading}
              className="w-full py-2 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-xs transition flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
            >
              {loading ? <RotateCw className="h-4 w-4 animate-spin" /> : <FlaskConical className="h-4 w-4" />}
              <span>Recalculate P-Value</span>
            </button>
          </div>
        </div>
      </div>

      {/* Test Results Card */}
      {testResult && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 p-6 rounded-2xl glass-card border border-slate-200 shadow-xs space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-500 uppercase">Test Type:</span>
                <span className="text-xs font-bold text-slate-900">Welch&apos;s Two-Sample T-Test</span>
              </div>
              <span
                className={`text-xs font-bold px-2.5 py-1 rounded-full ${
                  testResult.significant
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'bg-amber-100 text-amber-800'
                }`}
              >
                {testResult.significant ? '✓ Statistically Significant (p < 0.05)' : 'Not Significant'}
              </span>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                <p className="text-[10px] text-slate-500 font-bold uppercase">Group: {testResult.groupA}</p>
                <p className="text-lg font-black text-slate-900 font-outfit mt-0.5">{testResult.groupAMean}</p>
                <p className="text-[10px] text-slate-400">Sample Mean</p>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                <p className="text-[10px] text-slate-500 font-bold uppercase">Group: {testResult.groupB}</p>
                <p className="text-lg font-black text-indigo-600 font-outfit mt-0.5">{testResult.groupBMean}</p>
                <p className="text-[10px] text-slate-400">Sample Mean</p>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                <p className="text-[10px] text-slate-500 font-bold uppercase">T-Statistic</p>
                <p className="text-lg font-black text-slate-900 font-outfit mt-0.5">{testResult.tStatistic}</p>
                <p className="text-[10px] text-slate-400">Test Score</p>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                <p className="text-[10px] text-slate-500 font-bold uppercase">P-Value</p>
                <p className="text-lg font-black text-purple-600 font-outfit mt-0.5">{testResult.pValue.toExponential(2)}</p>
                <p className="text-[10px] text-slate-400">Significance Level</p>
              </div>
            </div>

            {/* Plain English Conclusion */}
            <div className="p-4 rounded-xl bg-indigo-50 border border-indigo-100 text-xs text-indigo-950 space-y-1">
              <div className="flex items-center gap-1.5 font-bold">
                <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                <span>Executive Statistical Interpretation:</span>
              </div>
              <p className="text-slate-700 leading-relaxed">{testResult.conclusion}</p>
            </div>
          </div>

          {/* Side Guidance */}
          <div className="p-6 rounded-2xl glass-card border border-slate-200 shadow-xs flex flex-col justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900 font-outfit mb-2">Why This Step Matters</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Before throwing data into a black-box Machine Learning model, hypothesis tests verify whether patterns are real signals or random noise. 
              </p>
              <div className="mt-4 space-y-2 text-xs text-slate-600">
                <div className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                  <span>Null Hypothesis (H0): Means are identical</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-indigo-500" />
                  <span>Alt Hypothesis (H1): True variance detected</span>
                </div>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-500">
              Confidence Interval: 95% (Alpha = 0.05)
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
