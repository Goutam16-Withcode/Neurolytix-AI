'use client';

import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Table, 
  Layers, 
  Grid3X3, 
  Activity, 
  Sliders, 
  Sparkles, 
  ArrowRight, 
  Clock, 
  MessageSquare, 
  Box, 
  Hash, 
  PieChart 
} from 'lucide-react';
import { DatasetInfo } from '@/types';
import { api, ComprehensiveEDA } from '@/lib/api';

interface EDAStudioProps {
  dataset: DatasetInfo;
  onNextStep?: () => void;
}

export function EDAStudio({ dataset, onNextStep }: EDAStudioProps) {
  const [edaData, setEdaData] = useState<ComprehensiveEDA | null>(null);
  const [filterType, setFilterType] = useState<'all' | 'numeric' | 'correlation' | 'categorical' | 'timeseries' | 'text'>('all');
  const [selectedHistCol, setSelectedHistCol] = useState<string>('monthly_spend');

  useEffect(() => {
    api.getComprehensiveEDA().then((data) => {
      setEdaData(data);
      if (data.numericCharts && data.numericCharts.length > 0) {
        setSelectedHistCol(data.numericCharts[0].column);
      }
    });
  }, [dataset]);

  const activeNumeric = edaData?.numericCharts?.find((d) => d.column === selectedHistCol) || edaData?.numericCharts?.[0];

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="p-6 rounded-2xl bg-[#090D1A]/90 border border-white/10 backdrop-blur-2xl relative overflow-hidden shadow-xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-blue-600/15 via-blue-700/10 to-transparent blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="px-2.5 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-[11px] font-bold text-blue-400">
                Phase 2: Automated EDA
              </span>
              <span className="text-xs text-slate-400">•</span>
              <span className="text-xs text-slate-400 font-mono">{dataset.name}</span>
            </div>
            <h1 className="text-2xl font-black font-outfit text-white tracking-tight">
              Dynamic Visual Analytics by Data Type
            </h1>
            <p className="text-xs text-slate-400 max-w-2xl mt-1 leading-relaxed">
              Automated graph synthesis classifying all features into <strong>Numeric, Categorical, Time-Series, and NLP Text</strong>. Computer Vision modules removed as specified.
            </p>
          </div>

          {onNextStep && (
            <button
              onClick={onNextStep}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold shadow-lg shadow-blue-600/40 transition cursor-pointer self-start md:self-auto hover:scale-105 active:scale-95"
            >
              <span>Next: Autonomous Data Scientist</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Data Type Filter Pills */}
        <div className="mt-6 flex flex-wrap items-center gap-2 border-t border-white/10 pt-4">
          <button
            onClick={() => setFilterType('all')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer ${
              filterType === 'all'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white border border-white/5'
            }`}
          >
            All Visual Types
          </button>
          <button
            onClick={() => setFilterType('numeric')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer ${
              filterType === 'numeric'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white border border-white/5'
            }`}
          >
            <Hash className="h-3.5 w-3.5 text-blue-400" />
            <span>Numeric (Histograms & Boxplots)</span>
          </button>
          <button
            onClick={() => setFilterType('correlation')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer ${
              filterType === 'correlation'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white border border-white/5'
            }`}
          >
            <Grid3X3 className="h-3.5 w-3.5 text-blue-400" />
            <span>Correlation Heatmap</span>
          </button>
          <button
            onClick={() => setFilterType('categorical')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer ${
              filterType === 'categorical'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white border border-white/5'
            }`}
          >
            <PieChart className="h-3.5 w-3.5 text-blue-400" />
            <span>Categorical Distributions</span>
          </button>
          <button
            onClick={() => setFilterType('timeseries')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer ${
              filterType === 'timeseries'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white border border-white/5'
            }`}
          >
            <Clock className="h-3.5 w-3.5 text-blue-400" />
            <span>Time-Series Trends</span>
          </button>
          <button
            onClick={() => setFilterType('text')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer ${
              filterType === 'text'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white border border-white/5'
            }`}
          >
            <MessageSquare className="h-3.5 w-3.5 text-blue-400" />
            <span>NLP & Text Mining</span>
          </button>
        </div>
      </div>

      {/* 1. Numerical Visuals: Histograms & Box Plots */}
      {(filterType === 'all' || filterType === 'numeric') && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Histogram Chart */}
          <div className="lg:col-span-2 p-6 rounded-2xl bg-[#090D1A]/90 border border-white/10 backdrop-blur-2xl shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-white font-outfit flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-blue-400" />
                  <span>Numeric Distribution Histogram: <span className="text-blue-400">{activeNumeric?.column}</span></span>
                </h3>
                <p className="text-xs text-slate-400">10-bin frequency distribution across {dataset.rows?.toLocaleString()} rows</p>
              </div>

              <select
                value={selectedHistCol}
                onChange={(e) => setSelectedHistCol(e.target.value)}
                className="px-3 py-1.5 rounded-xl border border-white/10 bg-[#0B1020] text-xs font-bold text-white focus:outline-none focus:border-blue-500"
              >
                {edaData?.numericCharts?.map((d) => (
                  <option key={d.column} value={d.column}>
                    {d.column}
                  </option>
                ))}
              </select>
            </div>

            {/* Glowing Histogram Visualization */}
            <div className="h-60 flex items-end gap-2.5 pt-6 pb-2 px-4 bg-[#05070F] rounded-xl border border-white/5">
              {activeNumeric?.histogram?.map((bin, idx) => {
                const maxCount = Math.max(...activeNumeric.histogram.map((b) => b.count));
                const heightPct = Math.round((bin.count / maxCount) * 100);
                return (
                  <div key={idx} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end group">
                    <span className="text-[10px] font-bold text-blue-300 opacity-0 group-hover:opacity-100 transition">
                      {bin.count}
                    </span>
                    <div
                      className="w-full bg-gradient-to-t from-blue-600 to-cyan-400 group-hover:from-blue-500 group-hover:to-cyan-300 rounded-t-md transition-all duration-300 shadow-[0_0_15px_rgba(37,99,235,0.3)]"
                      style={{ height: `${heightPct}%` }}
                    />
                    <span className="text-[9px] text-slate-500 truncate max-w-full font-mono">
                      {bin.range}
                    </span>
                  </div>
                );
              })}
            </div>

            <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-white/5">
              <span>Mean: <strong className="text-white font-mono">{activeNumeric?.mean}</strong></span>
              <span>Std Dev: <strong className="text-white font-mono">{activeNumeric?.std}</strong></span>
              <span>Skewness: <strong className="text-white font-mono">{activeNumeric?.skewness}</strong></span>
            </div>
          </div>

          {/* Box Plot & Outlier Statistics */}
          <div className="p-6 rounded-2xl bg-[#090D1A]/90 border border-white/10 backdrop-blur-2xl shadow-xl space-y-4 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-sm font-bold text-white font-outfit">Box Plot & Outlier Range</h4>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 border border-rose-500/30">
                  {activeNumeric?.boxplot.outliersCount} Outliers
                </span>
              </div>
              <p className="text-xs text-slate-400">Interquartile Range (Q1 to Q3) for {activeNumeric?.column}</p>

              <div className="space-y-2 mt-4 text-xs font-mono">
                <div className="flex justify-between p-2 rounded bg-white/5">
                  <span className="text-slate-400">Maximum (Q3 + 1.5 IQR):</span>
                  <span className="text-white font-bold">{activeNumeric?.boxplot.max}</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-white/5">
                  <span className="text-slate-400">Upper Quartile (Q3 75%):</span>
                  <span className="text-white font-bold">{activeNumeric?.boxplot.q3}</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-blue-500/10 border border-blue-500/20">
                  <span className="text-blue-300 font-bold">Median (Q2 50%):</span>
                  <span className="text-blue-300 font-black">{activeNumeric?.boxplot.median}</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-white/5">
                  <span className="text-slate-400">Lower Quartile (Q1 25%):</span>
                  <span className="text-white font-bold">{activeNumeric?.boxplot.q1}</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-white/5">
                  <span className="text-slate-400">Minimum (Q1 - 1.5 IQR):</span>
                  <span className="text-white font-bold">{activeNumeric?.boxplot.min}</span>
                </div>
              </div>
            </div>

            <p className="text-[11px] text-slate-500">
              💡 Outliers detected outside 1.5x IQR boundary. Ready for smart trimming in the scientist phase.
            </p>
          </div>
        </div>
      )}

      {/* 2. Correlation Heatmap */}
      {(filterType === 'all' || filterType === 'correlation') && (
        <div className="p-6 rounded-2xl bg-[#090D1A]/90 border border-white/10 backdrop-blur-2xl shadow-xl space-y-4">
          <div>
            <h3 className="text-sm font-bold text-white font-outfit flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-blue-400" />
              <span>Pearson Correlation Heatmap Matrix</span>
            </h3>
            <p className="text-xs text-slate-400">Multivariate collinearity & interaction strength (-1.0 to +1.0)</p>
          </div>

          <div className="overflow-x-auto rounded-xl border border-white/10 bg-[#05070F] p-4">
            <table className="w-full text-center text-xs font-mono">
              <thead>
                <tr>
                  <th className="p-2 text-left text-slate-400 font-bold">Features</th>
                  {edaData?.correlationMatrix?.columns?.map((c) => (
                    <th key={c} className="p-2 text-slate-300 font-bold whitespace-nowrap">
                      {c}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {edaData?.correlationMatrix?.columns?.map((rowCol, rIdx) => (
                  <tr key={rowCol}>
                    <td className="p-2 text-left font-bold text-slate-300 whitespace-nowrap border-r border-white/10">
                      {rowCol}
                    </td>
                    {edaData?.correlationMatrix?.columns?.map((colCol, cIdx) => {
                      const val = edaData.correlationMatrix.values[rIdx]?.[cIdx] ?? (rIdx === cIdx ? 1 : 0.35);
                      const isHigh = Math.abs(val) > 0.6;
                      const isSelf = rIdx === cIdx;
                      return (
                        <td
                          key={colCol}
                          className="p-2.5"
                          style={{
                            backgroundColor: isSelf 
                              ? 'rgba(37, 99, 235, 0.4)' 
                              : val > 0 
                              ? `rgba(37, 99, 235, ${Math.abs(val) * 0.7})` 
                              : `rgba(244, 63, 94, ${Math.abs(val) * 0.7})`
                          }}
                        >
                          <span className={`font-bold ${isHigh || isSelf ? 'text-white' : 'text-slate-300'}`}>
                            {val.toFixed(2)}
                          </span>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 3. Categorical Distributions */}
      {(filterType === 'all' || filterType === 'categorical') && (
        <div className="p-6 rounded-2xl bg-[#090D1A]/90 border border-white/10 backdrop-blur-2xl shadow-xl space-y-4">
          <div>
            <h3 className="text-sm font-bold text-white font-outfit flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-blue-400" />
              <span>Categorical Frequency Breakdown</span>
            </h3>
            <p className="text-xs text-slate-400">Class imbalance & cardinality verification across discrete features</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {edaData?.categoricalCharts?.map((cat) => (
              <div key={cat.column} className="p-4 rounded-xl bg-white/[0.03] border border-white/5 space-y-3">
                <div className="flex justify-between items-center text-xs font-bold">
                  <span className="text-white font-mono">{cat.column}</span>
                  <span className="text-slate-400 font-mono">{cat.distinctCount} unique classes</span>
                </div>

                <div className="space-y-2">
                  {cat.distribution.map((item) => (
                    <div key={item.label} className="space-y-1">
                      <div className="flex justify-between text-[11px]">
                        <span className="text-slate-300 font-medium">{item.label}</span>
                        <span className="text-slate-400 font-mono">{item.percentage}% ({item.count})</span>
                      </div>
                      <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-blue-600 to-cyan-400 rounded-full"
                          style={{ width: `${item.percentage}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 4. Time-Series Trends */}
      {(filterType === 'all' || filterType === 'timeseries') && (
        <div className="p-6 rounded-2xl bg-[#090D1A]/90 border border-white/10 backdrop-blur-2xl shadow-xl space-y-4">
          <div>
            <h3 className="text-sm font-bold text-white font-outfit flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-blue-400" />
              <span>Temporal Trends & Seasonality: <span className="text-blue-400">{edaData?.timeSeriesChart?.dateColumn}</span></span>
            </h3>
            <p className="text-xs text-slate-400">Aggregated trajectory over time across the target metric</p>
          </div>

          <div className="h-56 flex items-end gap-2 pt-6 pb-2 px-4 bg-[#05070F] rounded-xl border border-white/5">
            {edaData?.timeSeriesChart?.points?.map((pt, idx) => {
              const maxVal = Math.max(...edaData.timeSeriesChart.points.map((p) => p.value));
              const heightPct = Math.round((pt.value / maxVal) * 100);
              return (
                <div key={idx} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end group">
                  <span className="text-[10px] font-bold text-blue-300 opacity-0 group-hover:opacity-100 transition">
                    {pt.value}
                  </span>
                  <div
                    className="w-full bg-gradient-to-t from-blue-600 to-indigo-400 group-hover:from-blue-400 group-hover:to-indigo-300 rounded-t-sm transition-all"
                    style={{ height: `${heightPct}%` }}
                  />
                  <span className="text-[9px] text-slate-500 truncate max-w-full font-mono">
                    {pt.date.split('-')[1]}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 5. NLP & Text Mining */}
      {(filterType === 'all' || filterType === 'text') && (
        <div className="p-6 rounded-2xl bg-[#090D1A]/90 border border-white/10 backdrop-blur-2xl shadow-xl space-y-4">
          <div>
            <h3 className="text-sm font-bold text-white font-outfit flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-blue-400" />
              <span>NLP Word Cloud & Keyword Frequency Mining</span>
            </h3>
            <p className="text-xs text-slate-400">Lexical tokens extracted across unstructured text fields</p>
          </div>

          <div className="flex flex-wrap gap-2.5 p-5 bg-[#05070F] rounded-xl border border-white/5">
            {edaData?.nlpWordCloud?.map((word, idx) => (
              <span
                key={word.term}
                className="px-3.5 py-1.5 rounded-full border text-xs font-mono font-bold transition hover:scale-110 cursor-pointer"
                style={{
                  backgroundColor: idx % 2 === 0 ? 'rgba(37, 99, 235, 0.15)' : 'rgba(56, 189, 248, 0.15)',
                  borderColor: idx % 2 === 0 ? 'rgba(37, 99, 235, 0.3)' : 'rgba(56, 189, 248, 0.3)',
                  color: idx % 2 === 0 ? '#93C5FD' : '#7DD3FC',
                  fontSize: `${Math.max(11, Math.min(16, 10 + word.weight * 0.15))}px`
                }}
              >
                {word.term} <span className="opacity-60 text-[10px]">({word.weight})</span>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
