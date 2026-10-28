# Neurolytix AI 🧠

**Neurolytix AI** is a next-generation automated machine learning, data intelligence, and **Agentic RAG decision engine** designed for both non-technical business users and data scientists. 

Featuring a modern **Aceternity UI-inspired light theme** on **Next.js**, it transforms raw data into verified executive decisions, automated ML models, and high-FPS visual analytics.

---

## 🚀 Key Features

* **⚖️ Agentic RAG & JEV Decision Room**: Multi-agent consensus engine (Proposers ➔ Verifier ➔ JEV Judge) that audits tabular facts, eliminates hallucinations, and delivers verified business action plans.
* **🤖 1-Click AutoML Tournament**: Automated tournament between CatBoost, LightGBM, XGBoost, and Random Forest with live progress and ROC-AUC leaderboards.
* **✨ Aceternity UI Light Theme**: Radiant pastel Aurora glows, Bento Grid layouts, shimmer badges, and translucent frosted glass cards.
* **👥 Everyday User Friendly**: 1-click sample datasets, plain-English insight translations, and a "Pro Mode" toggle for deep SHAP / hyperparameter tuning.
* **💬 AI Copilot Drawer**: Natural language conversational assistant grounded directly in the dataset.
* **📊 Comprehensive Health & Quality Scan**: Automated missing value imputation, outlier spotter (Isolation Forest), and fairness auditing.
* **📝 Boardroom PDF Dossiers**: One-click executive report compilation.

---

## 🛠️ Quick Start

### 1. Launch Full-Stack Studio (Recommended)
Double-click `run_fullstack.bat` or run:

```bash
# Terminal 1: Python FastAPI API Server
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Next.js Frontend
cd web
npm run dev
```

Open your browser to **`http://localhost:3000`** to access the Next.js Studio.

---

## 📁 Architecture & Project Structure

* `web/`: Next.js 16+ React 19 App Router frontend with Aceternity UI and Tailwind CSS.
  * `src/app/page.tsx`: Main studio entry point.
  * `src/components/bento-hub.tsx`: Bento grid health and model showcase.
  * `src/components/decision-room.tsx`: Agentic RAG & JEV consensus decision engine.
  * `src/components/automl-studio.tsx`: AutoML tournament and feature importance explainability.
  * `src/components/dataset-studio.tsx`: Data ingestion and interactive table explorer.
  * `src/components/ai-copilot-drawer.tsx`: Natural language AI copilot.
  * `src/components/reports-hub.tsx`: One-click executive PDF report generator.
* `server.py`: FastAPI server bridging Next.js to Python data science algorithms.
* `src/`: 32 core Python modules:
  * `jev_decision_engine.py`: Agentic RAG and JEV deliberation engine.
  * `automl.py`: XGBoost, LightGBM, and CatBoost pipelines.
  * `offline_rag.py`: Offline vector embeddings and retrieval.
  * `dataset_intelligence.py` & `cleaning.py`: Automated quality scanning and imputation.
  * `agents.py` & `autonomous.py`: Autonomous AI data scientist agents.
* `app.py`: Legacy Streamlit interface (accessible via `streamlit run app.py`).
