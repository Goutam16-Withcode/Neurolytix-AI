export type DatasetType = 'tabular' | 'timeseries' | 'multimodal';

export interface DatasetColumn {
  name: string;
  type: 'numeric' | 'categorical' | 'datetime' | 'text';
  missingCount: number;
  uniqueCount: number;
  mean?: number;
  min?: number;
  max?: number;
  sampleValues: (string | number)[];
}

export interface DatasetInfo {
  id: string;
  name: string;
  rows: number;
  columns: number;
  sizeKb: number;
  healthScore: number;
  anomalyCount: number;
  missingCells: number;
  columnList: DatasetColumn[];
  previewRows: Record<string, any>[];
  suggestedTarget?: string;
  suggestedTask?: 'classification' | 'regression' | 'forecasting';
}

export interface AutoMLModel {
  id: string;
  name: string;
  family: 'XGBoost' | 'LightGBM' | 'CatBoost' | 'RandomForest' | 'Ensemble';
  task: 'classification' | 'regression';
  metricName: string;
  metricValue: number;
  trainTimeSeconds: number;
  status: 'trained' | 'training' | 'queued' | 'failed';
  isChampion?: boolean;
  featureImportance: { feature: string; weight: number }[];
}

export interface AgentProposal {
  agentRole: string;
  agentName: string;
  strategyTitle: string;
  recommendation: string;
  projectedImpact: string;
  riskRating: 'Low' | 'Medium' | 'High';
}

export interface JEVDecisionResult {
  query: string;
  retrievedContextCount: number;
  evidenceSnippets: string[];
  proposals: AgentProposal[];
  verifierReport: {
    passed: boolean;
    hallucinationsDetected: number;
    dataGroundingScore: number;
    notes: string;
  };
  evaluatorScores: {
    feasibility: number;
    roiImpact: number;
    ethicalFairness: number;
    overallConfidence: number;
  };
  finalDecision: {
    selectedStrategy: string;
    actionableSteps: string[];
    confidencePct: number;
    executiveRationale: string;
  };
}
