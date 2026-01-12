# Neurolytix AI 🧠

**Neurolytix AI** is a comprehensive, automated machine learning and data intelligence platform designed to streamline the data science workflow. Built with Streamlit, it offers an intuitive interface for everything from exploratory data analysis (EDA) to advanced multimodal learning.

## 🚀 Features

*   **📊 Advanced EDA**: Automated statistical testing, correlation heatmaps, and interactive visualizations.
*   **🤖 AutoML Engine**: Automated model training and hyperparameter tuning using XGBoost, LightGBM, and CatBoost.
*   **👁️ Multimodal Intelligence**: Support for image processing (CV), audio analysis, and cross-modal learning.
*   **🧹 Data Cleaning & Quality**: Intelligent missing value imputation, outlier detection (IQR, Isolation Forest, LOF), and fairness auditing.
*   **📉 Time Series Forecasting**: Prophet-based forecasting integration.
*   **📝 Automated Reporting**: Generate PDF reports of your analysis.
*   **🧠 LLM Integration**: Hypothesis generation, causal analysis, and insights powered by modern LLMs.
*   **🌐 Kaggle Integration**: Direct dataset download from Kaggle Hub.

## 🛠️ Installation

1.  **Clone the repository** (if applicable):
    ```bash
    git clone <repository-url>
    cd ML-auto
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ Usage

Run the application using Streamlit:

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501` to access the dashboard.

## 📁 Project Structure

*   `app.py`: Main entry point for the Streamlit application.
*   `src/`: Source code modules.
    *   `automl.py`: Automated Machine Learning logic.
    *   `eda.py`: Exploratory Data Analysis tools.
    *   `multimodal_advanced.py`: Advanced image/audio processing.
    *   `stats.py`: Statistical testing and outlier detection.
    *   `ui.py`: UI components and styling.
    *   ... (and many more specialized modules)
*   `requirements.txt`: Python dependencies.
