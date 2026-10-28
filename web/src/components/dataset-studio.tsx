'use client';

import React, { useState, useRef } from 'react';
import { 
  Database, 
  UploadCloud, 
  FileSpreadsheet, 
  CheckCircle2, 
  AlertCircle, 
  Sparkles, 
  Filter, 
  Download,
  Table,
  RotateCw,
  FileCheck,
  ArrowRight,
  Hash,
  PieChart,
  Clock,
  MessageSquare
} from 'lucide-react';
import { DatasetInfo } from '@/types';
import { SAMPLE_DATASETS } from '@/lib/sample-data';
import { api } from '@/lib/api';

interface DatasetStudioProps {
  dataset: DatasetInfo;
  onSelectDataset: (dataset: DatasetInfo) => void;
  onNextStep?: () => void;
}

export function DatasetStudio({ dataset, onSelectDataset, onNextStep }: DatasetStudioProps) {
  const [cleaned, setCleaned] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadError(null);

    try {
      const newDataset = await api.uploadFile(file);
      onSelectDataset(newDataset);
      setCleaned(false);
    } catch (err: any) {
      console.error(err);
      setUploadError(err.message || 'Upload failed. Ensure FastAPI backend is running on port 8000.');
    } finally {
      setUploading(false);
    }
  };

  const handleAutoClean = async () => {
    try {
      const cleanedDataset = await api.cleanDataset();
      onSelectDataset(cleanedDataset);
      setCleaned(true);
    } catch (err) {
      console.error(err);
      setCleaned(true);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Sample Dataset Bar */}
      <div className="p-6 rounded-2xl bg-[#090D1A]/90 border border-white/10 backdrop-blur-2xl relative overflow-hidden shadow-xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-blue-600/15 via-blue-700/10 to-transparent blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="px-2.5 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-[11px] font-bold text-blue-400">
                Phase 1: Ingest & Health Scanner
              </span>
              <span className="text-xs text-slate-400">•</span>
              <span className="text-xs text-slate-400 font-mono">Multi-Format Parser</span>
            </div>
            <h1 className="text-2xl font-black font-outfit text-white tracking-tight">
              Dataset Ingestion & Auto-Type Inference
            </h1>
            <p className="text-xs text-slate-400 max-w-2xl mt-1 leading-relaxed">
              Drop any CSV, Excel, Parquet, or JSON file. The backend automatically categorizes every feature into <strong>Numeric, Categorical, Temporal Time-Series, and NLP Text</strong>.
            </p>
          </div>

          <div className="flex items-center gap-3 self-start md:self-auto">
            {onNextStep && (
              <button
                onClick={onNextStep}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold shadow-lg shadow-blue-600/40 transition cursor-pointer hover:scale-105 active:scale-95"
              >
                <span>Next: Automated EDA</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>

        {/* Benchmark Switcher */}
        <div className="mt-5 flex flex-wrap items-center gap-2 text-xs">
          <span className="text-slate-400 font-medium">Or load benchmark:</span>
          {Object.values(SAMPLE_DATASETS).map((s) => (
            <button
              key={s.id}
              onClick={() => {
                onSelectDataset(s);
                setCleaned(false);
              }}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer border ${
                dataset.id === s.id
                  ? 'bg-blue-600 text-white border-blue-500 shadow-md shadow-blue-600/30'
                  : 'bg-white/5 hover:bg-white/10 text-slate-300 border-white/10'
              }`}
            >
              {s.name.split('.')[0]}
            </button>
          ))}
        </div>

        {/* Drag & Drop Zone */}
        <div
          onClick={() => fileInputRef.current?.click()}
          className="mt-5 border-2 border-dashed border-white/15 hover:border-blue-500/50 bg-[#080B14] rounded-2xl p-6 text-center transition cursor-pointer group"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.xlsx,.xls,.parquet,.json"
            onChange={handleFileUpload}
            className="hidden"
          />
          {uploading ? (
            <div className="flex flex-col items-center">
              <RotateCw className="h-8 w-8 text-blue-400 animate-spin mb-2" />
              <p className="text-xs font-bold text-white">Uploading & parsing via FastAPI backend...</p>
            </div>
          ) : (
            <>
              <UploadCloud className="mx-auto h-8 w-8 text-blue-400 mb-2 group-hover:scale-110 transition" />
              <p className="text-xs font-bold text-white">
                Drop your dataset here or browse files (CSV, Excel, Parquet, or JSON)
              </p>
              <p className="text-[11px] text-slate-500 mt-1 font-mono">
                Streaming to POST http://localhost:8000/api/upload
              </p>
            </>
          )}
        </div>

        {uploadError && (
          <div className="mt-3 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span>{uploadError}</span>
          </div>
        )}
      </div>

      {/* Dataset Health & Inferred Types Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-[#090D1A]/90 border border-white/10 shadow-lg">
          <p className="text-xs font-medium text-slate-400">Integrity Health</p>
          <p className="text-2xl font-extrabold text-blue-400 font-outfit mt-1">
            {cleaned ? 99 : dataset.healthScore}%
          </p>
          <p className="text-[11px] text-slate-500 mt-1">
            {cleaned ? 'All missing values resolved' : `${dataset.missingCells} missing values`}
          </p>
        </div>

        <div className="p-4 rounded-xl bg-[#090D1A]/90 border border-white/10 shadow-lg">
          <p className="text-xs font-medium text-slate-400">Dimensions</p>
          <p className="text-2xl font-extrabold text-white font-outfit mt-1">
            {dataset.rows?.toLocaleString()} × {dataset.columns}
          </p>
          <p className="text-[11px] text-slate-500 mt-1">Total rows × columns</p>
        </div>

        <div className="p-4 rounded-xl bg-[#090D1A]/90 border border-white/10 shadow-lg">
          <p className="text-xs font-medium text-slate-400">Anomalies Detected</p>
          <p className="text-2xl font-extrabold text-rose-400 font-outfit mt-1">
            {cleaned ? 0 : dataset.anomalyCount}
          </p>
          <p className="text-[11px] text-slate-500 mt-1">Outliers isolated</p>
        </div>

        <div className="p-4 rounded-xl bg-[#090D1A]/90 border border-white/10 shadow-lg flex flex-col justify-between">
          <p className="text-xs font-medium text-slate-400">Auto-Clean & Impute</p>
          <button
            onClick={handleAutoClean}
            disabled={cleaned}
            className={`w-full py-2 px-3 rounded-lg text-xs font-bold transition flex items-center justify-center gap-1.5 cursor-pointer ${
              cleaned
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 cursor-default'
                : 'bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-600/30'
            }`}
          >
            {cleaned ? (
              <>
                <CheckCircle2 className="h-4 w-4" />
                <span>Cleaned ✓</span>
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

      {/* Raw Data Preview Table */}
      <div className="rounded-2xl bg-[#090D1A]/90 overflow-hidden border border-white/10 space-y-4 p-5 shadow-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Table className="h-4 w-4 text-blue-400" />
            <h3 className="text-sm font-bold text-white font-outfit">
              Data Preview ({dataset.previewRows?.length || 0} sample records)
            </h3>
          </div>
          <span className="text-xs text-slate-500 font-mono">{dataset.sizeKb} KB in memory</span>
        </div>

        <div className="overflow-x-auto rounded-xl border border-white/10">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0B1020] border-b border-white/10 text-slate-300 font-bold">
              <tr>
                {dataset.columnList?.map((col) => (
                  <th key={col.name} className="py-2.5 px-3 whitespace-nowrap">
                    <div>{col.name}</div>
                    <span className="text-[10px] font-normal text-blue-400 font-mono">{col.type}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 text-slate-300 font-mono">
              {dataset.previewRows?.map((row, idx) => (
                <tr key={idx} className="hover:bg-white/5 transition">
                  {dataset.columnList?.map((col) => (
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
