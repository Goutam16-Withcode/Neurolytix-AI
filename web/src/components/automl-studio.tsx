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
  ArrowRight, 
  Zap, 
  RotateCw,
  Clock,
  MessageSquare,
  Layers,
  Send,
  Code2,
  Rocket
} from 'lucide-react';
import { AutoMLModel, DatasetInfo } from '@/types';
import { api, LivePredictionResult } from '@/lib/api';
import confetti from 'canvas-confetti';

interface AutoMLStudioProps {
  dataset: DatasetInfo;
  models: AutoMLModel[];
  proMode: boolean;
  onNextStep?: () => void;
}

export function AutoMLStudio({ dataset, models: initialModels, proMode, onNextStep }: AutoMLStudioProps) {
  const [modelCategory, setModelCategory] = useState<'tabular' | 'timeseries' | 'nlp'>('tabular');
  const [selectedTarget, setSelectedTarget] = useState(dataset.suggestedTarget || 'churned');
  const [models, setModels] = useState<AutoMLModel[]>(initialModels);
  const [isTraining, setIsTraining] = useState(false);
  const [trainProgress, setTrainProgress] = useState(100);
  const [activeModel, setActiveModel] = useState<AutoMLModel>(initialModels[0]);

  // Deployment Simulator State
  const [testTickets, setTestTickets] = useState<number>(3);
  const [testSpend, setTestSpend] = useState<number>(115.0);
  const [testContract, setTestContract] = useState<string>('Month-to-Month');
  const [predictionResult, setPredictionResult] = useState<LivePredictionResult | null>({
    prediction: "Yes (High Churn Risk)",
    churnProbability: 84.2,
    confidenceScore: 84.2,
    inferenceTimeMs: 4.8,
    championAlgorithm: "CatBoost v4.2"
  });
  const [predicting, setPredicting] = useState(false);

  const handleStartTraining = async () => {
    setIsTraining(true);
    setTrainProgress(20);

    const progressTimer = setInterval(() => {
      setTrainProgress((p) => (p >= 85 ? 85 : p + 20));
    }, 300);

    try {
      const realModels = await api.trainModelSuite(modelCategory, selectedTarget);
      clearInterval(progressTimer);
      setTrainProgress(100);
      setModels(realModels);
      if (realModels.length > 0) {
        setActiveModel(realModels[0]);
      }
      try {
        confetti({
          particleCount: 50,
          spread: 60,
          origin: { y: 0.6 }
        });
      } catch (e) {
        // ignore
      }
    } catch (e) {
      console.error(e);
      clearInterval(progressTimer);
    } finally {
      setIsTraining(false);
    }
  };

  const handleLivePredict = async () => {
    setPredicting(true);
    try {
      const result = await api.livePredict({
        support_tickets: testTickets,
        monthly_spend: testSpend,
        contract_type: testContract
      });
      setPredictionResult(result);
    } catch (e) {
      console.error(e);
    } finally {
      setPredicting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="p-6 rounded-2xl bg-[#090D1A]/90 border border-white/10 backdrop-blur-2xl relative overflow-hidden shadow-xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-blue-600/15 via-blue-700/10 to-transparent blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="px-2.5 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-[11px] font-bold text-blue-400">
                Phase 4 & 5: Model Design, Training & Deployment
              </span>
              <span className="text-xs text-slate-400">•</span>
              <span className="text-xs text-slate-400 font-mono">CV Removed • ML/NLP/Time-Series</span>
            </div>
            <h1 className="text-2xl font-black font-outfit text-white tracking-tight">
              Multi-Algorithm Studio & Deployment Simulator
            </h1>
            <p className="text-xs text-slate-400 max-w-2xl mt-1 leading-relaxed">
              Train algorithms matched to your data type: <strong>Tabular ML (CatBoost, LightGBM, XGBoost)</strong>, <strong>Time-Series Forecasting (Prophet, ARIMA)</strong>, or <strong>NLP Text Classification</strong>.
            </p>
          </div>

          <div className="flex items-center gap-2.5 self-start md:self-auto">
            {onNextStep && (
              <button
                onClick={onNextStep}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold shadow-lg shadow-blue-600/40 transition cursor-pointer hover:scale-105 active:scale-95"
              >
                <span>Next: Agentic RAG Decision Room</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>

        {/* Algorithm Suite Switcher */}
        <div className="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-white/10 pt-4">
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setModelCategory('tabular');
                setSelectedTarget('churned');
              }}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold transition cursor-pointer ${
                modelCategory === 'tabular'
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                  : 'bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white border border-white/5'
              }`}
            >
              <Cpu className="h-3.5 w-3.5 text-blue-300" />
              <span>Tabular ML Suite (CatBoost / LightGBM / XGBoost)</span>
            </button>

            <button
              onClick={() => {
                setModelCategory('timeseries');
                setSelectedTarget('monthly_spend');
              }}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold transition cursor-pointer ${
                modelCategory === 'timeseries'
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                  : 'bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white border border-white/5'
              }`}
            >
              <Clock className="h-3.5 w-3.5 text-blue-300" />
              <span>Time-Series Suite (Prophet / ARIMA)</span>
            </button>

            <button
              onClick={() => {
                setModelCategory('nlp');
                setSelectedTarget('churned');
              }}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold transition cursor-pointer ${
                modelCategory === 'nlp'
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                  : 'bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white border border-white/5'
              }`}
            >
              <MessageSquare className="h-3.5 w-3.5 text-blue-300" />
              <span>NLP Suite (Classifiers)</span>
            </button>
          </div>

          <button
            onClick={handleStartTraining}
            disabled={isTraining}
            className="flex items-center gap-2 px-5 py-2 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold shadow-md shadow-blue-600/40 transition cursor-pointer disabled:opacity-50"
          >
            {isTraining ? <RotateCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
            <span>{isTraining ? `Training ${trainProgress}%...` : 'Train Model Suite'}</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Leaderboard on Left, Deployment Simulator on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Model Tournament Table & Confusion Matrix */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white font-outfit flex items-center gap-2">
              <Trophy className="h-4 w-4 text-amber-400" />
              <span>Algorithm Leaderboard Tournament</span>
            </h3>
            <span className="text-xs text-slate-400">Click a model to inspect weights</span>
          </div>

          <div className="rounded-2xl bg-[#090D1A]/90 border border-white/10 overflow-hidden shadow-xl">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-[#0B1020] border-b border-white/10 text-slate-400 font-bold uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-3 px-4">Algorithm</th>
                  <th className="py-3 px-4">Architecture</th>
                  <th className="py-3 px-4">Validation Metric</th>
                  <th className="py-3 px-4">Performance Score</th>
                  <th className="py-3 px-4 text-right">Latency</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-slate-300">
                {models.map((model, idx) => {
                  const isSelected = activeModel.id === model.id;
                  return (
                    <tr
                      key={model.id}
                      onClick={() => setActiveModel(model)}
                      className={`hover:bg-white/5 transition cursor-pointer ${
                        isSelected ? 'bg-blue-600/20 font-medium' : ''
                      }`}
                    >
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span className="text-slate-500 font-bold font-sans">#{idx + 1}</span>
                          <span className="font-bold text-white font-sans">{model.name}</span>
                          {model.isChampion && (
                            <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                              Champion
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded bg-white/5 text-slate-300 text-[11px]">
                          {model.family}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-400 font-sans">{model.metricName}</td>
                      <td className="py-3 px-4 font-bold text-blue-400 text-sm">
                        {(model.metricValue * 100).toFixed(1)}%
                      </td>
                      <td className="py-3 px-4 text-right text-slate-400">
                        {model.trainTimeSeconds}s
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Confusion Matrix (for Tabular Classification) */}
          {activeModel.confusionMatrix && (
            <div className="p-5 rounded-2xl bg-[#090D1A]/90 border border-white/10 space-y-3 shadow-xl">
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                Confusion Matrix: {activeModel.name}
              </h4>
              <div className="grid grid-cols-2 gap-3 max-w-sm font-mono text-center text-xs">
                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
                  <p className="text-[10px] text-slate-400">True Positive (TP)</p>
                  <p className="text-base font-black mt-1">{activeModel.confusionMatrix.tp}</p>
                </div>
                <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300">
                  <p className="text-[10px] text-slate-400">False Positive (FP)</p>
                  <p className="text-base font-black mt-1">{activeModel.confusionMatrix.fp}</p>
                </div>
                <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300">
                  <p className="text-[10px] text-slate-400">False Negative (FN)</p>
                  <p className="text-base font-black mt-1">{activeModel.confusionMatrix.fn}</p>
                </div>
                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
                  <p className="text-[10px] text-slate-400">True Negative (TN)</p>
                  <p className="text-base font-black mt-1">{activeModel.confusionMatrix.tn}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Col: Live Model Deployment & Real-Time Prediction Simulator */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white font-outfit flex items-center gap-2">
              <Rocket className="h-4 w-4 text-blue-400" />
              <span>Model Deployment & Live Simulator</span>
            </h3>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              Live on :8000
            </span>
          </div>

          <div className="p-5 rounded-2xl bg-[#090D1A]/90 border border-white/10 space-y-4 shadow-xl">
            <div className="space-y-3 text-xs">
              <div>
                <div className="flex justify-between text-slate-300 mb-1">
                  <span>Support Tickets:</span>
                  <span className="font-mono font-bold text-blue-400">{testTickets} tickets</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="8"
                  value={testTickets}
                  onChange={(e) => setTestTickets(Number(e.target.value))}
                  className="w-full accent-blue-500 cursor-pointer"
                />
              </div>

              <div>
                <div className="flex justify-between text-slate-300 mb-1">
                  <span>Monthly Spend:</span>
                  <span className="font-mono font-bold text-blue-400">${testSpend}/mo</span>
                </div>
                <input
                  type="range"
                  min="20"
                  max="350"
                  value={testSpend}
                  onChange={(e) => setTestSpend(Number(e.target.value))}
                  className="w-full accent-blue-500 cursor-pointer"
                />
              </div>

              <div>
                <label className="text-slate-300 block mb-1">Contract Type:</label>
                <select
                  value={testContract}
                  onChange={(e) => setTestContract(e.target.value)}
                  className="w-full p-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs font-medium focus:outline-none focus:border-blue-500"
                >
                  <option value="Month-to-Month">Month-to-Month (Higher Risk)</option>
                  <option value="One-Year">One-Year Contract</option>
                  <option value="Two-Year">Two-Year Contract (Stable)</option>
                </select>
              </div>

              <button
                onClick={handleLivePredict}
                disabled={predicting}
                className="w-full py-2.5 rounded-xl bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-bold text-xs shadow-md shadow-blue-600/30 transition flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
              >
                {predicting ? <RotateCw className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                <span>Run Real-Time Inference</span>
              </button>
            </div>

            {/* Prediction Output Card */}
            {predictionResult && (
              <div className="p-4 rounded-xl bg-white/[0.03] border border-white/10 space-y-2 font-mono text-xs">
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Prediction:</span>
                  <span className="font-bold text-amber-300 font-sans">{predictionResult.prediction}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Churn Probability:</span>
                  <span className="font-bold text-rose-400">{predictionResult.churnProbability}%</span>
                </div>
                <div className="flex justify-between items-center text-[10px] text-slate-500 pt-1 border-t border-white/5">
                  <span>Engine: {predictionResult.championAlgorithm}</span>
                  <span className="text-emerald-400">⚡ {predictionResult.inferenceTimeMs}ms</span>
                </div>
              </div>
            )}

            {/* Deployment Snippet */}
            <div className="pt-2">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider flex items-center gap-1.5 mb-1.5 font-bold">
                <Code2 className="h-3 w-3 text-blue-400" />
                <span>Production REST Endpoint</span>
              </span>
              <pre className="p-2.5 rounded-lg bg-[#05070F] border border-white/5 text-[10px] text-slate-300 font-mono overflow-x-auto">
{`curl -X POST http://localhost:8000/api/model/predict \\
  -H "Content-Type: application/json" \\
  -d '{"support_tickets": ${testTickets}, "monthly_spend": ${testSpend}}'`}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
