import { DatasetInfo, AutoMLModel, JEVDecisionResult } from '@/types';

export const SAMPLE_DATASETS: Record<string, DatasetInfo> = {
  'ecommerce-churn': {
    id: 'ecommerce-churn',
    name: 'Customer Retention & Churn Prediction.csv',
    rows: 4820,
    columns: 9,
    sizeKb: 342,
    healthScore: 94,
    anomalyCount: 16,
    missingCells: 24,
    suggestedTarget: 'churned',
    suggestedTask: 'classification',
    columnList: [
      { name: 'customer_id', type: 'text', missingCount: 0, uniqueCount: 4820, sampleValues: ['CUST-1042', 'CUST-8921', 'CUST-3312'] },
      { name: 'tenure_months', type: 'numeric', missingCount: 0, uniqueCount: 72, mean: 32.4, min: 1, max: 72, sampleValues: [12, 48, 6, 24] },
      { name: 'monthly_spend', type: 'numeric', missingCount: 12, uniqueCount: 1420, mean: 78.5, min: 18.2, max: 210.0, sampleValues: [64.5, 115.0, 45.2, 89.9] },
      { name: 'support_tickets', type: 'numeric', missingCount: 0, uniqueCount: 9, mean: 1.8, min: 0, max: 8, sampleValues: [0, 2, 4, 1] },
      { name: 'contract_type', type: 'categorical', missingCount: 0, uniqueCount: 3, sampleValues: ['Month-to-Month', '1 Year', '2 Year'] },
      { name: 'payment_method', type: 'categorical', missingCount: 0, uniqueCount: 4, sampleValues: ['Credit Card', 'Bank Transfer', 'Electronic Check'] },
      { name: 'satisfaction_score', type: 'numeric', missingCount: 12, uniqueCount: 5, mean: 3.7, min: 1, max: 5, sampleValues: [4, 5, 2, 3] },
      { name: 'last_login_days', type: 'numeric', missingCount: 0, uniqueCount: 90, mean: 8.2, min: 0, max: 88, sampleValues: [2, 14, 0, 5] },
      { name: 'churned', type: 'categorical', missingCount: 0, uniqueCount: 2, sampleValues: ['No', 'Yes', 'No', 'No'] },
    ],
    previewRows: [
      { customer_id: 'CUST-1001', tenure_months: 18, monthly_spend: 74.2, support_tickets: 1, contract_type: 'Month-to-Month', payment_method: 'Credit Card', satisfaction_score: 4, last_login_days: 3, churned: 'No' },
      { customer_id: 'CUST-1002', tenure_months: 4, monthly_spend: 112.5, support_tickets: 5, contract_type: 'Month-to-Month', payment_method: 'Electronic Check', satisfaction_score: 1, last_login_days: 28, churned: 'Yes' },
      { customer_id: 'CUST-1003', tenure_months: 42, monthly_spend: 52.0, support_tickets: 0, contract_type: '2 Year', payment_method: 'Bank Transfer', satisfaction_score: 5, last_login_days: 1, churned: 'No' },
      { customer_id: 'CUST-1004', tenure_months: 9, monthly_spend: 96.8, support_tickets: 3, contract_type: 'Month-to-Month', payment_method: 'Credit Card', satisfaction_score: 2, last_login_days: 15, churned: 'Yes' },
      { customer_id: 'CUST-1005', tenure_months: 60, monthly_spend: 145.0, support_tickets: 1, contract_type: '1 Year', payment_method: 'Credit Card', satisfaction_score: 5, last_login_days: 2, churned: 'No' },
      { customer_id: 'CUST-1006', tenure_months: 2, monthly_spend: 42.1, support_tickets: 4, contract_type: 'Month-to-Month', payment_method: 'Electronic Check', satisfaction_score: 2, last_login_days: 34, churned: 'Yes' },
    ]
  },
  'medical-risk': {
    id: 'medical-risk',
    name: 'Cardiovascular Risk Diagnostics.csv',
    rows: 3200,
    columns: 8,
    sizeKb: 215,
    healthScore: 98,
    anomalyCount: 8,
    missingCells: 0,
    suggestedTarget: 'cardio_risk',
    suggestedTask: 'classification',
    columnList: [
      { name: 'patient_id', type: 'text', missingCount: 0, uniqueCount: 3200, sampleValues: ['PT-402', 'PT-591'] },
      { name: 'age', type: 'numeric', missingCount: 0, uniqueCount: 45, mean: 53.2, min: 28, max: 74, sampleValues: [48, 62, 55, 34] },
      { name: 'blood_pressure', type: 'numeric', missingCount: 0, uniqueCount: 60, mean: 128.4, min: 95, max: 180, sampleValues: [120, 142, 130, 115] },
      { name: 'cholesterol_level', type: 'numeric', missingCount: 0, uniqueCount: 95, mean: 214.2, min: 140, max: 320, sampleValues: [195, 240, 210, 180] },
      { name: 'bmi', type: 'numeric', missingCount: 0, uniqueCount: 50, mean: 27.6, min: 18.5, max: 41.2, sampleValues: [24.8, 31.2, 28.0, 22.4] },
      { name: 'smoking_status', type: 'categorical', missingCount: 0, uniqueCount: 3, sampleValues: ['Non-Smoker', 'Former Smoker', 'Active Smoker'] },
      { name: 'physical_activity', type: 'categorical', missingCount: 0, uniqueCount: 3, sampleValues: ['High', 'Moderate', 'Low'] },
      { name: 'cardio_risk', type: 'categorical', missingCount: 0, uniqueCount: 2, sampleValues: ['Low', 'High', 'Moderate'] }
    ],
    previewRows: [
      { patient_id: 'PT-402', age: 58, blood_pressure: 145, cholesterol_level: 248, bmi: 29.4, smoking_status: 'Active Smoker', physical_activity: 'Low', cardio_risk: 'High' },
      { patient_id: 'PT-403', age: 39, blood_pressure: 118, cholesterol_level: 182, bmi: 23.1, smoking_status: 'Non-Smoker', physical_activity: 'High', cardio_risk: 'Low' },
      { patient_id: 'PT-404', age: 64, blood_pressure: 152, cholesterol_level: 270, bmi: 32.0, smoking_status: 'Former Smoker', physical_activity: 'Low', cardio_risk: 'High' },
      { patient_id: 'PT-405', age: 47, blood_pressure: 125, cholesterol_level: 205, bmi: 26.5, smoking_status: 'Non-Smoker', physical_activity: 'Moderate', cardio_risk: 'Low' },
    ]
  }
};

export const SAMPLE_MODELS: AutoMLModel[] = [
  {
    id: 'm1',
    name: 'NeuroCatBoost v4.2',
    family: 'CatBoost',
    task: 'classification',
    metricName: 'ROC-AUC',
    metricValue: 0.948,
    trainTimeSeconds: 4.2,
    status: 'trained',
    isChampion: true,
    featureImportance: [
      { feature: 'support_tickets', weight: 0.38 },
      { feature: 'last_login_days', weight: 0.27 },
      { feature: 'monthly_spend', weight: 0.19 },
      { feature: 'tenure_months', weight: 0.11 },
      { feature: 'contract_type', weight: 0.05 },
    ]
  },
  {
    id: 'm2',
    name: 'LightGBM Turbo',
    family: 'LightGBM',
    task: 'classification',
    metricName: 'ROC-AUC',
    metricValue: 0.934,
    trainTimeSeconds: 2.1,
    status: 'trained',
    featureImportance: [
      { feature: 'support_tickets', weight: 0.34 },
      { feature: 'last_login_days', weight: 0.29 },
      { feature: 'monthly_spend', weight: 0.21 },
      { feature: 'tenure_months', weight: 0.10 },
      { feature: 'contract_type', weight: 0.06 },
    ]
  },
  {
    id: 'm3',
    name: 'XGBoost DeepOpt',
    family: 'XGBoost',
    task: 'classification',
    metricName: 'ROC-AUC',
    metricValue: 0.927,
    trainTimeSeconds: 3.8,
    status: 'trained',
    featureImportance: [
      { feature: 'support_tickets', weight: 0.36 },
      { feature: 'monthly_spend', weight: 0.25 },
      { feature: 'last_login_days', weight: 0.22 },
      { feature: 'tenure_months', weight: 0.12 },
      { feature: 'contract_type', weight: 0.05 },
    ]
  },
  {
    id: 'm4',
    name: 'Balanced Random Forest',
    family: 'RandomForest',
    task: 'classification',
    metricName: 'ROC-AUC',
    metricValue: 0.892,
    trainTimeSeconds: 1.6,
    status: 'trained',
    featureImportance: [
      { feature: 'support_tickets', weight: 0.31 },
      { feature: 'monthly_spend', weight: 0.28 },
      { feature: 'tenure_months', weight: 0.18 },
      { feature: 'last_login_days', weight: 0.15 },
      { feature: 'contract_type', weight: 0.08 },
    ]
  }
];

export const SAMPLE_JEV_DECISION: JEVDecisionResult = {
  query: "What is the single highest-impact strategy to cut customer churn by at least 25% over the next 60 days?",
  retrievedContextCount: 142,
  evidenceSnippets: [
    "Correlating support_tickets >= 3 with churn shows an 81.4% churn rate vs 8.2% baseline.",
    "Customers on Month-to-Month contracts experiencing support ticket escalations churn within an average of 14 days.",
    "High-value monthly spenders ($95+) have 3.2x higher sensitivity to unresolved support tickets."
  ],
  proposals: [
    {
      agentRole: 'Growth & Retention Agent',
      agentName: 'Aria (Revenue Lead)',
      strategyTitle: 'Proactive VIP Ticket Rescue & Escalation Protocol',
      recommendation: 'Trigger immediate automated outreach and assigned senior support representative for any customer submitting >= 2 tickets in 14 days, coupled with a $20 service credit.',
      projectedImpact: '-32% Churn among customers with support friction',
      riskRating: 'Low'
    },
    {
      agentRole: 'Pricing & Finance Agent',
      agentName: 'Marcus (Financial Strategist)',
      strategyTitle: 'Annual Contract Discount Incentivization',
      recommendation: 'Offer 20% discount to all Month-to-Month subscribers if they convert to an Annual agreement.',
      projectedImpact: '-18% Overall churn via contract lock-in',
      riskRating: 'Medium'
    },
    {
      agentRole: 'Product & UX Agent',
      agentName: 'Chloe (Product Lead)',
      strategyTitle: 'In-App Re-Engagement Notification Blitz',
      recommendation: 'Target users with last_login_days > 15 with automated promotional email sequences.',
      projectedImpact: '-11% Inactivity Churn',
      riskRating: 'Low'
    }
  ],
  verifierReport: {
    passed: true,
    hallucinationsDetected: 0,
    dataGroundingScore: 98.4,
    notes: "Verified: Customers with 3+ support tickets account for 61% of total churned records in the 4,820 rows. Numbers match dataset ground truth perfectly."
  },
  evaluatorScores: {
    feasibility: 96,
    roiImpact: 94,
    ethicalFairness: 99,
    overallConfidence: 96.5
  },
  finalDecision: {
    selectedStrategy: "Strategy 1: Proactive VIP Ticket Rescue & Escalation Protocol (Recommended by JEV Judge)",
    actionableSteps: [
      "Set an automated webhook trigger when support_tickets counter increments to 2.",
      "Route customer instantly to Tier-2 specialized retention agents with priority queue placement.",
      "Apply a 1-month loyalty credit ($20) or complimentary plan upgrade before the customer churns.",
      "Track cohort retention on the Live Drift & Monitoring tab."
    ],
    confidencePct: 96.5,
    executiveRationale: "The data demonstrates that unresolved support friction is the #1 churn catalyst (38% feature importance in champion CatBoost model). Implementing the VIP Rescue protocol delivers the fastest measurable ROI within 60 days with minimal operational risk."
  }
};
