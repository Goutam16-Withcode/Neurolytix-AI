'use client';

import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from '@/context/auth-context';
import { FrontPage } from '@/components/front-page';
import { AuthModal } from '@/components/auth-modal';
import { Navigation } from '@/components/navigation';
import { DatasetStudio } from '@/components/dataset-studio';
import { EDAStudio } from '@/components/eda-studio';
import { ScientistStudio } from '@/components/scientist-studio';
import { AutoMLStudio } from '@/components/automl-studio';
import { DecisionRoom } from '@/components/decision-room';
import { ReportsHub } from '@/components/reports-hub';
import { AICopilotDrawer } from '@/components/ai-copilot-drawer';
import { SAMPLE_DATASETS, SAMPLE_MODELS, SAMPLE_JEV_DECISION } from '@/lib/sample-data';
import { DatasetInfo, AutoMLModel, JEVDecisionResult } from '@/types';
import { api, HealthStatus } from '@/lib/api';
import { AlertTriangle, Check, ArrowLeft, Sparkles } from 'lucide-react';

function StudioApp() {
  const { user, loginAsGuest } = useAuth();
  const [currentView, setCurrentView] = useState<'front' | 'studio'>('front');
  const [activeTab, setActiveTab] = useState<string>('data');
  const [dataset, setDataset] = useState<DatasetInfo>(SAMPLE_DATASETS['ecommerce-churn']);
  const [models, setModels] = useState<AutoMLModel[]>(SAMPLE_MODELS);
  const [decisionResult, setDecisionResult] = useState<JEVDecisionResult>(SAMPLE_JEV_DECISION);
  const [isCopilotOpen, setIsCopilotOpen] = useState<boolean>(false);
  const [backendHealth, setBackendHealth] = useState<HealthStatus>({ online: false, latencyMs: 0 });

  useEffect(() => {
    const pingBackend = async () => {
      const status = await api.checkHealth();
      setBackendHealth(status);
      if (status.online) {
        try {
          const remoteDataset = await api.getDataset();
          if (remoteDataset && remoteDataset.rows) {
            setDataset(remoteDataset);
          }
        } catch (e) {
          console.warn('Could not sync remote dataset', e);
        }
      }
    };

    pingBackend();
    const interval = setInterval(pingBackend, 5000);
    return () => clearInterval(interval);
  }, []);

  const pipelineSteps = [
    { id: 'data', label: '1. Ingest Data' },
    { id: 'eda', label: '2. Dynamic EDA' },
    { id: 'scientist', label: '3. Data Scientist' },
    { id: 'automl', label: '4. Model & Deploy' },
    { id: 'jev', label: '5. JEV Decisions' },
    { id: 'reports', label: '6. Executive Report' },
  ];

  // If user is on front page, render FrontPage
  if (currentView === 'front') {
    return (
      <>
        <FrontPage
          onLaunchStudio={() => {
            if (!user) loginAsGuest();
            setCurrentView('studio');
          }}
          onTrySample={(sampleKey) => {
            if (!user) loginAsGuest();
            if (sampleKey && SAMPLE_DATASETS[sampleKey as keyof typeof SAMPLE_DATASETS]) {
              setDataset(SAMPLE_DATASETS[sampleKey as keyof typeof SAMPLE_DATASETS]);
            }
            setCurrentView('studio');
          }}
        />
        <AuthModal onSuccess={() => setCurrentView('studio')} />
      </>
    );
  }

  // Main Dashboard Studio View (Retains the exact same theme and style)
  return (
    <div className="min-h-screen flex flex-col bg-[#030712] text-[#F8FAFC] selection:bg-blue-600/30 selection:text-blue-200 relative overflow-hidden">
      {/* Signature Celestial Sapphire Diffuse Glow for Dashboard (Identical to Front Page) */}
      <div className="pointer-events-none absolute -top-40 right-0 w-[700px] h-[700px] bg-gradient-to-br from-blue-600/20 via-blue-700/10 to-transparent blur-[140px] rounded-full" />
      <div className="pointer-events-none absolute bottom-0 right-1/4 w-[650px] h-[650px] bg-gradient-to-t from-blue-600/20 via-indigo-700/15 to-transparent blur-[150px] rounded-full" />

      {/* Top Header Navigation */}
      <Navigation
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        dataset={dataset}
        onOpenCopilot={() => setIsCopilotOpen(true)}
        backendHealth={backendHealth}
        onBackToHome={() => setCurrentView('front')}
      />

      {/* Backend Status Alert if offline */}
      {!backendHealth.online && (
        <div className="bg-amber-500/10 border-b border-amber-500/20 px-4 py-2 text-amber-300 text-xs">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-400 flex-shrink-0" />
              <span>
                <strong>FastAPI Backend Offline:</strong> Running with benchmarks. To connect live Python ML & EDA algorithms, run: <code className="bg-amber-500/20 px-2 py-0.5 rounded font-mono text-amber-200 font-bold">python -m uvicorn server:app --port 8000 --reload</code>
              </span>
            </div>
            <span className="text-[11px] font-semibold text-amber-400 animate-pulse font-mono">Auto-Reconnecting...</span>
          </div>
        </div>
      )}

      {/* Main Container */}
      <main className="flex-1 py-6 px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-7xl mx-auto space-y-6">

          {/* Active Lifecycle View */}
          {activeTab === 'data' && (
            <DatasetStudio
              dataset={dataset}
              onSelectDataset={(newDs) => setDataset(newDs)}
              onNextStep={() => setActiveTab('eda')}
            />
          )}

          {activeTab === 'eda' && (
            <EDAStudio
              dataset={dataset}
              onNextStep={() => setActiveTab('scientist')}
            />
          )}

          {activeTab === 'scientist' && (
            <ScientistStudio
              dataset={dataset}
              onNextStep={() => setActiveTab('automl')}
            />
          )}

          {activeTab === 'automl' && (
            <AutoMLStudio
              dataset={dataset}
              models={models}
              proMode={true}
              onNextStep={() => setActiveTab('jev')}
            />
          )}

          {activeTab === 'jev' && (
            <DecisionRoom
              dataset={dataset}
              initialResult={decisionResult}
              onNextStep={() => setActiveTab('reports')}
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
      </main>

      {/* AI Copilot Drawer */}
      <AICopilotDrawer
        isOpen={isCopilotOpen}
        onClose={() => setIsCopilotOpen(false)}
        dataset={dataset}
      />

      {/* Global Firebase Auth Modal */}
      <AuthModal onSuccess={() => setCurrentView('studio')} />
    </div>
  );
}

export default function Home() {
  return (
    <AuthProvider>
      <StudioApp />
    </AuthProvider>
  );
}
