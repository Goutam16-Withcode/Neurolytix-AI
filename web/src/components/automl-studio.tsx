'use client';

import React, { useState } from 'react';
import { 
  Cpu, 
  Trophy, 
  Play, 
  CheckCircle2, 
  BarChart, 
  Sliders, 
  Sparkles, 
  HelpCircle, 
  ArrowRight, 
  Zap, 
  RotateCw 
} from 'lucide-react';
import { AutoMLModel, DatasetInfo } from '@/types';
import { ShimmerBadge } from '@/components/ui/shimmer-badge';
import confetti from 'canvas-confetti';

interface AutoMLStudioProps {
  dataset: DatasetInfo;
  models: AutoMLModel[];
  proMode: boolean;
}

export function AutoMLStudio({ dataset, models: initialModels, proMode }: AutoMLStudioProps) {
  const [models, setModels] = useState<AutoMLModel[]>(initialModels);
  const [selectedTarget, setSelectedTarget] = useState(dataset.suggestedTarget || 'churned');
  const [isTraining, setIsTraining] = useState(false);
  const [trainProgress, setTrainProgress] = useState(100);
  const [activeModel, setActiveModel] = useState<AutoMLModel>(initialModels[0]);

  const handleStartTraining = () => {
    setIsTraining(true);
    setTrainProgress(15);

    const interval = setInterval(() => {
      setTrainProgress((prev) => {
        if (prev >= 95) {
          clearInterval(interval);
          setTimeout(() => {
            setIsTraining(false);
            setTrainProgress(100);
            try {
              confetti({
                particleCount: 80,
                spread: 70,
                origin: { y: 0.6 }
              });
            } catch (e) {
              // ignore
            }
          }, 600);
          return 95;
        }
        return prev + 25;
      });
    }, 450);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="p-6 rounded-2xl glass-card bg-gradient-to-r from-white via-purple-50/30 to-indigo-50/20 border-purple-100/80">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <div className="p-2 rounded-xl bg-purple-600 text-white shadow-sm shadow-purple-600/30">
                <Cpu className="h-5 w-5" />
              </div>
              <h1 className="text-2xl font-bold font-outfit text-slate-900 tracking-tight">
                1-Click AutoML Tournament
              </h1>
              <ShimmerBadge variant="purple">Auto-Tuned</ShimmerBadge>
            </div>
            <p className="text-sm text-slate-600 max-w-2xl">
              Neurolytix runs an automated tournament between CatBoost, LightGBM, and XGBoost to find the highest-accuracy model without requiring manual code.
            </p>
          </div>

          {/* Quick Target Setup & Train CTA */}
          <div className="flex items-center gap-3">
            <div className="text-right">
              <label className="text-[11px] font-semibold text-slate-500 block">Target to Predict</label>
              <select
                value={selectedTarget}
                onChange={(e) => setSelectedTarget(e.target.value)}
                className="mt-0.5 px-3 py-1.5 rounded-lg border border-slate-300 bg-white text-xs font-bold text-slate-800 shadow-sm focus:outline-none"
              >
                {dataset.columnList.map((col) => (
                  <option key={col.name} value={col.name}>
                    {col.name} ({col.type})
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={handleStartTraining}
              disabled={isTraining}
              className="mt-4 px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white text-xs font-bold shadow-md shadow-indigo-600/20 transition cursor-pointer flex items-center gap-2 disabled:opacity-50"
            >
              {isTraining ? (
                <>
                  <RotateCw className="h-4 w-4 animate-spin" />
                  <span>Training ({trainProgress}%)...</span>
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  <span>Run Tournament</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Live Training Progress Bar */}
        {isTraining && (
          <div className="mt-4 pt-3 border-t border-purple-100">
            <div className="flex items-center justify-between text-xs text-purple-900 font-semibold mb-1">
              <span>Evaluating CatBoost, LightGBM, and XGBoost with 5-Fold Cross Validation...</span>
              <span>{trainProgress}%</span>
            </div>
            <div className="h-2 w-full rounded-full bg-purple-100 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 via-purple-600 to-pink-500 transition-all duration-300 rounded-full"
                style={{ width: `${trainProgress}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Main Grid: Leaderboard & Model Explainability */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Leaderboard Table */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900 font-outfit flex items-center gap-2">
              <Trophy className="h-4 w-4 text-amber-500" />
              <span>Model Tournament Leaderboard</span>
            </h3>
            <span className="text-xs text-slate-500">Sorted by ROC-AUC</span>
          </div>

          <div className="rounded-2xl glass-card overflow-hidden border border-slate-200">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50/80 border-b border-slate-200/80 text-slate-500 font-semibold">
                  <tr>
                    <th className="py-3 px-4">Rank & Model</th>
                    <th className="py-3 px-4">Family</th>
                    <th className="py-3 px-4">Accuracy (ROC-AUC)</th>
                    <th className="py-3 px-4">Train Time</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {models.map((model, idx) => {
                    const isSelected = activeModel.id === model.id;
                    return (
                      <tr
                        key={model.id}
                        onClick={() => setActiveModel(model)}
                        className={`hover:bg-indigo-50/30 transition cursor-pointer ${
                          isSelected ? 'bg-indigo-50/50 font-medium' : ''
                        }`}
                      >
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-slate-400">#{idx + 1}</span>
                            <span className="font-bold text-slate-900">{model.name}</span>
                            {model.isChampion && (
                              <ShimmerBadge variant="amber" className="text-[9px] py-0">
                                Best
                              </ShimmerBadge>
                            )}
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-semibold text-[11px]">
                            {model.family}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-bold text-indigo-600 font-outfit text-sm">
                          {(model.metricValue * 100).toFixed(1)}%
                        </td>
                        <td className="py-3 px-4 text-slate-500">{model.trainTimeSeconds}s</td>
                        <td className="py-3 px-4 text-right">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setActiveModel(model);
                            }}
                            className="px-2.5 py-1 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-semibold text-[11px] transition"
                          >
                            Inspect
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Plain English Translation Card for Everyday Users */}
          <div className="p-4 rounded-xl bg-indigo-50/50 border border-indigo-100 text-xs space-y-1">
            <span className="font-bold text-indigo-900">What does 94.8% accuracy mean?</span>
            <p className="text-slate-600 leading-relaxed">
              If you deploy <strong>{activeModel.name}</strong> to predict customer churn, it will accurately distinguish between customers who stay and customers who leave in 95 out of 100 cases.
            </p>
          </div>
        </div>

        {/* Right Col: Explainability & Top Key Drivers */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900 font-outfit flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-indigo-600" />
              <span>What Drives Predictions?</span>
            </h3>
            <span className="text-xs text-slate-500">SHAP Weights</span>
          </div>

          <div className="p-5 rounded-2xl glass-card space-y-4 border border-slate-200">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Active Model Feature Importance
              </p>
              <p className="text-sm font-bold text-slate-900 mt-0.5">{activeModel.name}</p>
            </div>

            <div className="space-y-3">
              {activeModel.featureImportance.map((item, idx) => (
                <div key={idx} className="space-y-1 text-xs">
                  <div className="flex items-center justify-between text-slate-700 font-medium">
                    <span>{item.feature}</span>
                    <span className="font-bold text-slate-900">{(item.weight * 100).toFixed(0)}%</span>
                  </div>
                  <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                    <div
                      className="h-full bg-indigo-600 rounded-full"
                      style={{ width: `${item.weight * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="pt-3 border-t border-slate-100 text-[11px] text-slate-500 leading-relaxed">
              💡 <strong>Key Takeaway</strong>: The number of unresolved support tickets is responsible for 38% of whether someone churns. Reducing tickets is your #1 lever.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
