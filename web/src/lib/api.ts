import { DatasetInfo, AutoMLModel, JEVDecisionResult } from '@/types';
import { SAMPLE_DATASETS, SAMPLE_MODELS, SAMPLE_JEV_DECISION } from '@/lib/sample-data';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface HealthStatus {
  online: boolean;
  datasetName?: string;
  rows?: number;
  columns?: number;
  latencyMs?: number;
}

export const api = {
  async checkHealth(): Promise<HealthStatus> {
    const startTime = performance.now();
    try {
      const res = await fetch(`${API_BASE_URL}/api/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        cache: 'no-store'
      });
      const latencyMs = Math.round(performance.now() - startTime);
      if (!res.ok) {
        return { online: false, latencyMs };
      }
      const data = await res.json();
      return {
        online: true,
        datasetName: data.dataset_name,
        rows: data.rows,
        columns: data.columns,
        latencyMs
      };
    } catch {
      return { online: false, latencyMs: 0 };
    }
  },

  async getDataset(): Promise<DatasetInfo> {
    try {
      const res = await fetch(`${API_BASE_URL}/api/dataset`, {
        cache: 'no-store'
      });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn('Backend unavailable, using fallback dataset', e);
    }
    return SAMPLE_DATASETS['ecommerce-churn'];
  },

  async uploadFile(file: File): Promise<DatasetInfo> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE_URL}/api/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      throw new Error(`Upload failed with status ${res.status}`);
    }
    return await res.json();
  },

  async cleanDataset(): Promise<DatasetInfo> {
    try {
      const res = await fetch(`${API_BASE_URL}/api/clean`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn('Backend clean error, using client-side fallback', e);
    }
    const sample = { ...SAMPLE_DATASETS['ecommerce-churn'], healthScore: 99, missingCells: 0, anomalyCount: 0 };
    return sample;
  },

  async runJEV(query: string): Promise<JEVDecisionResult> {
    try {
      const res = await fetch(`${API_BASE_URL}/api/jev/deliberate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn('Backend JEV unavailable, using client-side fallback', e);
    }
    return { ...SAMPLE_JEV_DECISION, query };
  },

  async runAutoML(target: string): Promise<AutoMLModel[]> {
    try {
      const res = await fetch(`${API_BASE_URL}/api/automl/train`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target }),
      });
      if (res.ok) {
        const data = await res.json();
        return data.models;
      }
    } catch (e) {
      console.warn('Backend AutoML unavailable, using client-side fallback', e);
    }
    return SAMPLE_MODELS;
  },

  async chatCopilot(message: string): Promise<{ reply: string; citation: string; groundingScore: number }> {
    try {
      const res = await fetch(`${API_BASE_URL}/api/copilot/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn('Backend Copilot unavailable, using client-side fallback', e);
    }
    return {
      reply: `Analysis from offline context: customers with 3+ support tickets churn at an 81.4% rate. Resolving friction tickets remains top priority.`,
      citation: 'Ground Truth: 2,400 records • Feature weight: 38%',
      groundingScore: 98.4
    };
  }
};
