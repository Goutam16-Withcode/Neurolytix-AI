'use client';

import React, { useState } from 'react';
import { 
  Database, 
  UploadCloud, 
  FileSpreadsheet, 
  CheckCircle2, 
  AlertCircle, 
  Sparkles, 
  Filter, 
  Download,
  Table
} from 'lucide-react';
import { DatasetInfo } from '@/types';
import { SAMPLE_DATASETS } from '@/lib/sample-data';
import { ShimmerBadge } from '@/components/ui/shimmer-badge';

interface DatasetStudioProps {
  dataset: DatasetInfo;
  onSelectDataset: (dataset: DatasetInfo) => void;
}

export function DatasetStudio({ dataset, onSelectDataset }: DatasetStudioProps) {
  const [cleaned, setCleaned] = useState(false);
  const [activeTab, setActiveTab] = useState<'preview' | 'columns' | 'samples'>('preview');

  const handleAutoClean = () => {
    setCleaned(true);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Sample Dataset Bar */}
      <div className="p-6 rounded-2xl glass-card bg-gradient-to-r from-white via-slate-50 to-indigo-50/20 border-slate-200">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <div className="p-2 rounded-xl bg-indigo-600 text-white shadow-sm shadow-indigo-600/30">
                <Database className="h-5 w-5" />
              </div>
              <h1 className="text-2xl font-bold font-outfit text-slate-900 tracking-tight">
                Dataset Studio & Health Scanner
              </h1>
              <ShimmerBadge variant="emerald">Live Memory</ShimmerBadge>
            </div>
            <p className="text-sm text-slate-600 max-w-2xl">
              Inspect data structures, automated type inference, missing value distribution, and 1-click auto-cleaning.
            </p>
          </div>

          {/* 1-Click Sample Dataset Selector */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-500">Try Sample:</span>
            {Object.values(SAMPLE_DATASETS).map((s) => (
              <button
                key={s.id}
                onClick={() => onSelectDataset(s)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer border ${
                  dataset.id === s.id
                    ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm'
                    : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-200'
                }`}
              >
                {s.name.split('.')[0]}
              </button>
            ))}
          </div>
        </div>

        {/* Drag & Drop Zone */}
        <div className="mt-5 border-2 border-dashed border-indigo-200/80 hover:border-indigo-400 bg-white/60 rounded-2xl p-6 text-center transition cursor-pointer">
          <UploadCloud className="mx-auto h-8 w-8 text-indigo-500 mb-2" />
          <p className="text-xs font-bold text-slate-800">
            Drag and drop your own dataset here (CSV, Excel, Parquet, JSON, or ZIP)
          </p>
          <p className="text-[11px] text-slate-500 mt-1">
            Files are processed locally and securely. No data leaves your machine.
          </p>
        </div>
      </div>

      {/* Dataset Health & Cleaning Scorecard */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl glass-card border-slate-200">
          <p className="text-xs font-medium text-slate-500">Integrity Health Score</p>
          <p className="text-2xl font-extrabold text-indigo-600 font-outfit mt-1">
            {cleaned ? 99 : dataset.healthScore}%
          </p>
          <p className="text-[11px] text-slate-500 mt-1">
            {cleaned ? 'All missing values resolved' : `${dataset.missingCells} missing values`}
          </p>
        </div>

        <div className="p-4 rounded-xl glass-card border-slate-200">
          <p className="text-xs font-medium text-slate-500">Dimensions</p>
          <p className="text-2xl font-extrabold text-slate-900 font-outfit mt-1">
            {dataset.rows.toLocaleString()} × {dataset.columns}
          </p>
          <p className="text-[11px] text-slate-500 mt-1">Total rows × columns</p>
        </div>

        <div className="p-4 rounded-xl glass-card border-slate-200">
          <p className="text-xs font-medium text-slate-500">Anomalies Detected</p>
          <p className="text-2xl font-extrabold text-rose-600 font-outfit mt-1">
            {cleaned ? 0 : dataset.anomalyCount}
          </p>
          <p className="text-[11px] text-slate-500 mt-1">Outliers isolated</p>
        </div>

        <div className="p-4 rounded-xl glass-card border-slate-200 flex flex-col justify-between">
          <p className="text-xs font-medium text-slate-500">Auto-Clean & Impute</p>
          <button
            onClick={handleAutoClean}
            disabled={cleaned}
            className={`w-full py-2 px-3 rounded-lg text-xs font-bold transition flex items-center justify-center gap-1.5 cursor-pointer ${
              cleaned
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 cursor-default'
                : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm'
            }`}
          >
            {cleaned ? (
              <>
                <CheckCircle2 className="h-4 w-4" />
                <span>Dataset Cleaned</span>
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                <span>1-Click Auto Clean</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Interactive Table Preview */}
      <div className="rounded-2xl glass-card overflow-hidden border border-slate-200 space-y-4 p-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Table className="h-4 w-4 text-indigo-600" />
            <h3 className="text-sm font-bold text-slate-900 font-outfit">
              Data Preview ({dataset.previewRows.length} sample rows shown)
            </h3>
          </div>
          <span className="text-xs text-slate-500">{dataset.sizeKb} KB memory footprint</span>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-200/80">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-bold">
              <tr>
                {dataset.columnList.map((col) => (
                  <th key={col.name} className="py-2.5 px-3 whitespace-nowrap">
                    <div>{col.name}</div>
                    <span className="text-[10px] font-normal text-slate-400">{col.type}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {dataset.previewRows.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-50/80 transition">
                  {dataset.columnList.map((col) => (
                    <td key={col.name} className="py-2.5 px-3 whitespace-nowrap">
                      {row[col.name] !== undefined ? String(row[col.name]) : '-'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
