'use client';

import React, { useState } from 'react';
import { AuroraBackground } from '@/components/ui/aurora-background';
import { Navigation } from '@/components/navigation';
import { BentoHub } from '@/components/bento-hub';
import { DatasetStudio } from '@/components/dataset-studio';
import { AutoMLStudio } from '@/components/automl-studio';
import { DecisionRoom } from '@/components/decision-room';
import { ReportsHub } from '@/components/reports-hub';
import { AICopilotDrawer } from '@/components/ai-copilot-drawer';
import { SAMPLE_DATASETS, SAMPLE_MODELS, SAMPLE_JEV_DECISION } from '@/lib/sample-data';
import { DatasetInfo, AutoMLModel, JEVDecisionResult } from '@/types';
import { Sliders } from 'lucide-react';

export default function Home() {
  const [activeTab, setActiveTab] = useState<string>('bento');
  const [dataset, setDataset] = useState<DatasetInfo>(SAMPLE_DATASETS['ecommerce-churn']);
  const [models, setModels] = useState<AutoMLModel[]>(SAMPLE_MODELS);
  const [decisionResult, setDecisionResult] = useState<JEVDecisionResult>(SAMPLE_JEV_DECISION);
  const [proMode, setProMode] = useState<boolean>(false);
  const [isCopilotOpen, setIsCopilotOpen] = useState<boolean>(false);

  return (
    <div className="min-h-screen flex flex-col bg-[#ffffff] selection:bg-indigo-500/10 selection:text-indigo-600">
      {/* Top Header Navigation */}
      <Navigation
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        dataset={dataset}
        proMode={proMode}
        setProMode={setProMode}
        onOpenCopilot={() => setIsCopilotOpen(true)}
      />

      {/* Pro Mode Banner */}
      {proMode && (
        <div className="bg-indigo-600 text-white text-xs px-4 py-1.5 flex items-center justify-between shadow-inner">
          <div className="max-w-7xl mx-auto w-full flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sliders className="h-3.5 w-3.5" />
              <span className="font-semibold">
                Pro Mode Active: Advanced hyperparameters, cross-validation metrics, and SHAP explainability matrices enabled.
              </span>
            </div>
            <button
              onClick={() => setProMode(false)}
              className="text-[11px] underline hover:text-indigo-200 cursor-pointer"
            >
              Exit Pro Mode
            </button>
          </div>
        </div>
      )}

      {/* Main Content Body */}
      <main className="flex-1">
        <AuroraBackground className="min-h-[calc(100vh-4rem)] py-8 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            {activeTab === 'bento' && (
              <BentoHub
                dataset={dataset}
                models={models}
                decisionResult={decisionResult}
                onNavigateTab={(tab) => setActiveTab(tab)}
                onOpenCopilot={() => setIsCopilotOpen(true)}
              />
            )}

            {activeTab === 'data' && (
              <DatasetStudio
                dataset={dataset}
                onSelectDataset={(newDs) => setDataset(newDs)}
              />
            )}

            {activeTab === 'automl' && (
              <AutoMLStudio
                dataset={dataset}
                models={models}
                proMode={proMode}
              />
            )}

            {activeTab === 'jev' && (
              <DecisionRoom
                dataset={dataset}
                initialResult={decisionResult}
              />
            )}

            {activeTab === 'reports' && (
              <ReportsHub
                dataset={dataset}
                models={models}
                decisionResult={decisionResult}
              />
            )}
          </div>
        </AuroraBackground>
      </main>

      {/* Slide-out AI Data Agent Copilot */}
      <AICopilotDrawer
        isOpen={isCopilotOpen}
        onClose={() => setIsCopilotOpen(false)}
        dataset={dataset}
      />
    </div>
  );
}
