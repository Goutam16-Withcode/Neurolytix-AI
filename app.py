import streamlit as st
import importlib
import sys
import os
import time
import warnings
import pandas as pd
import pickle
import tempfile
import hashlib

# Suppress pkg_resources deprecation warning from xgboost
warnings.filterwarnings("ignore", message=".*pkg_resources is deprecated.*")

# Page Configuration
st.set_page_config(
    page_title="Neurolytix AI",
    page_icon="🧠",
    layout="wide"
)

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import ui
import data_loader
import eda
import visualization
import automl
import unsupervised
import cleaning
import llm_engine
import reporting
import stats
import feature_eng
import fairness
import deployment
import monitoring
import time_series
import dataset_intelligence
import collaborative
import multimodal
import hypothesis
import agents
import autonomous
import insights
import hyperopt
import interpretability
import ensemble
import reinforcement
import transfer_learning
import statistical_testing
import multimodal_advanced

# Removed global CSS call to enable dynamic routing
# ui.load_custom_css()

# Data persistence functions
def get_cache_dir():
    """Get cache directory for data persistence."""
    cache_dir = os.path.join(tempfile.gettempdir(), 'neurolytix_cache')
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

def save_data_cache(df, filename):
    """Save dataframe to cache."""
    if df is not None:
        cache_file = os.path.join(get_cache_dir(), f"{filename}.pkl")
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(df, f)
            return cache_file
        except Exception:
            pass
    return None

def load_data_cache(filename):
    """Load dataframe from cache."""
    cache_file = os.path.join(get_cache_dir(), f"{filename}.pkl")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        except Exception:
            pass
    return None

def get_file_hash(file):
    """Get hash of uploaded file for cache key."""
    if hasattr(file, 'getvalue'):
        return hashlib.md5(file.getvalue()).hexdigest()[:8]
    return None

def cleanup_old_cache(max_files=10):
    """Clean up old cache files to prevent disk space issues."""
    cache_dir = get_cache_dir()
    if os.path.exists(cache_dir):
        cache_files = [os.path.join(cache_dir, f) for f in os.listdir(cache_dir) if f.endswith('.pkl')]
        if len(cache_files) > max_files:
            # Sort by modification time, keep newest
            cache_files.sort(key=os.path.getmtime, reverse=True)
            files_to_remove = cache_files[max_files:]
            for file_path in files_to_remove:
                try:
                    os.remove(file_path)
                except Exception:
                    pass

def main():
    # Session State Initialization
    if 'df' not in st.session_state:
        st.session_state.df = None

    # Add refresh warning at the top
    if st.session_state.df is None:
        cache_files = [f for f in os.listdir(get_cache_dir()) if f.endswith('.pkl')] if os.path.exists(get_cache_dir()) else []
        if not cache_files:
            warning_placeholder = st.empty()
            warning_placeholder.warning("⚠️ **Browser Refresh Warning**: Refreshing this page will clear your current session. Data will be cached automatically after loading to prevent loss.")
            time.sleep(2.5)
            warning_placeholder.empty()

    # Check for cached data on startup
    if st.session_state.df is None:
        cache_files = [f for f in os.listdir(get_cache_dir()) if f.endswith('.pkl')] if os.path.exists(get_cache_dir()) else []
        if cache_files:
            st.sidebar.markdown("### 📂 Data Source")
            st.sidebar.info("💾 Previous session data detected!")

            # Show available cached datasets
            for cache_file in cache_files:
                dataset_name = cache_file.replace('.pkl', '')
                col1, col2 = st.sidebar.columns([3, 1])
                with col1:
                    st.write(f"📊 {dataset_name}")
                with col2:
                    if st.button(f"Load", key=f"load_{dataset_name}"):
                        cached_df = load_data_cache(dataset_name)
                        if cached_df is not None:
                            st.session_state.df = cached_df
                            st.sidebar.success(f"✅ Loaded {dataset_name} from cache!")
                            st.rerun()
                        else:
                            st.sidebar.error("Failed to load cached data")

            st.sidebar.markdown("---")
            st.sidebar.markdown("### 📂 Load New Data")
        else:
            st.sidebar.markdown("### 📂 Data Source")
    else:
        st.sidebar.markdown("### 📂 Data Source")
    
    data_source_options = ["Upload File", "Kaggle API"]
    # Local file auto-load and demo dataset options removed.

    data_source = st.sidebar.radio("Load Data From", data_source_options, label_visibility="collapsed")
    
    if data_source == "Upload File":
        uploaded_file = st.sidebar.file_uploader(
            "Upload Data Files (CSV, Excel, JSON, Parquet, ZIP, TAR.GZ, etc.)",
            type=["csv", "xlsx", "xls", "json", "parquet", "zip", "tar", "gz", "bz2"],
            help="Supports individual data files and compressed archives. Archives are automatically extracted."
        )
        if uploaded_file is not None:
            df = data_loader.load_data(uploaded_file)
            if df is not None:
                st.session_state.df = df
                # Cache the loaded data
                file_hash = get_file_hash(uploaded_file)
                cache_name = f"{uploaded_file.name}_{file_hash}" if file_hash else uploaded_file.name
                save_data_cache(df, cache_name)
                cleanup_old_cache()  # Clean up old cache files
                st.sidebar.success(f"💾 Data cached for future sessions!")

    elif data_source == "Kaggle API":
        kaggle_handle = st.sidebar.text_input("Kaggle Handle", placeholder="e.g. titanic")
        if st.sidebar.button("Download & Load"):
            if kaggle_handle:
                df = data_loader.load_from_kaggle(kaggle_handle)
                if df is not None:
                    st.session_state.df = df
                    # Cache the loaded data
                    save_data_cache(df, f"kaggle_{kaggle_handle}")
                    cleanup_old_cache()  # Clean up old cache files
                    st.sidebar.success("Kaggle Data Loaded!")
                    st.sidebar.success(f"💾 Data cached for future sessions!")
            else:
                st.sidebar.warning("Enter a handle.")
                
    if st.session_state.df is not None:
        st.sidebar.success(f"✅ Data Loaded: {st.session_state.df.shape}")
        st.sidebar.info("💡 **Tip**: Your data is cached. Refreshing the page will show recovery options.")

        if st.sidebar.button("❌ Clear Data"):
             st.session_state.df = None
             st.rerun()

        if st.sidebar.button("🗑️ Clear Cache"):
            import shutil
            cache_dir = get_cache_dir()
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir)
            st.sidebar.success("Cache cleared!")
            st.rerun()

    # Add session reset option
    if st.sidebar.button("🔄 Reset Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.sidebar.markdown("---")
    
    # Categorized Navigation System
    st.sidebar.markdown("### 🛠️ Neural Modules")
    
    navigation_map = {
        "📊 Core Analytics": ["Data Overview", "Visual Analytics", "Statistical Analysis", "Data Quality & Anomalies", "Time Series Analysis", "Dataset Intelligence"],
        "🧹 Data Engineering": ["Smart Cleaning", "Auto Feature Engineering"],
        "🤖 Machine Learning": ["AutoML (Supervised)", "Unsupervised Learning", "Fairness Checking"],
        "🚀 MLOps & Deploy": ["Model Deployment", "Data Drift Monitoring"],
        "🧠 Advanced AI": ["Multi-Modal Analysis", "AI Data Agent"],
        "🔬 Advanced ML Techniques": ["Model Interpretability", "Ensemble Methods", "Hyperparameter Optimization", "Reinforcement Learning", "Transfer Learning"],
        "📊 Statistical & Hypothesis Testing": ["Hypothesis Testing", "A/B Testing Framework", "Causal Inference", "Bayesian Statistics", "Baseline & Significance Checks"],
        "👥 Collaborative Analytics": ["Team Collaboration"],
        "🌐 Multi-Modal Intelligence": ["Text Analytics & NLP", "Image Processing & CV", "Audio Analysis"],
        "📈 Neuro Insights": ["AI Insights (Narrative)", "Autonomous Data Scientist", "Reporting", "Export & Reports"]
    }
    
    category = st.sidebar.selectbox("Select Suite", list(navigation_map.keys()))
    choice = st.sidebar.radio("Active Route", navigation_map[category])
    
    clean_choice = choice # No icons in the sub-list for cleaner routing
    
    st.sidebar.info(f"Route: {category} > {clean_choice}")
    
    # Load Dynamic Theme based on Route
    ui.load_custom_css(clean_choice)
    
    # Global Neon Header
    st.markdown(f"""
        <div class="neuro-header">
            <span style="color:var(--primary); filter: drop-shadow(0 0 10px var(--accent-glow));">NEUROLYTIX</span> AI PRO
        </div>
    """, unsafe_allow_html=True)
    # Handle quick navigation selections
    if 'selected_category' in st.session_state and 'selected_choice' in st.session_state:
        category = st.session_state['selected_category']
        choice = st.session_state['selected_choice']
        clean_choice = choice
        del st.session_state['selected_category']
        del st.session_state['selected_choice']

    # Route Breadcrumb
    st.markdown(f"""
        <div style="opacity: 0.5; font-size: 0.8rem; letter-spacing: 2px; margin-bottom: 20px; margin-top: -10px;">
            PLATFORM / {category.upper()} / {clean_choice.upper()}
        </div>
    """, unsafe_allow_html=True)

    # Routing
    if clean_choice == "Data Overview":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            eda.show_overview(st.session_state.df)
        
    elif clean_choice == "Visual Analytics":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            visualization.show_visualization(st.session_state.df)

    elif clean_choice == "Statistical Analysis":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            stats.show_stats(st.session_state.df)

    elif clean_choice == "Data Quality & Anomalies":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            stats.show_data_quality_dashboard(st.session_state.df)

    elif clean_choice == "Time Series Analysis":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            time_series.show_time_series_analysis(st.session_state.df)

    elif clean_choice == "Dataset Intelligence":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            dataset_intelligence.show_dataset_intelligence(st.session_state.df)
        
    elif clean_choice == "Smart Cleaning":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            cleaning.show_cleaning(st.session_state.df)

    elif clean_choice == "Auto Feature Engineering":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            feature_eng.generate_features(st.session_state.df)
        
    elif clean_choice == "AutoML (Supervised)":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            automl.show_automl(st.session_state.df)
        
    elif clean_choice == "Unsupervised Learning":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            unsupervised.show_unsupervised(st.session_state.df)

    elif clean_choice == "Fairness Checking":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            fairness.analyze_fairness(st.session_state.df)

    elif clean_choice == "Model Deployment":
        deployment.generate_deployment_package(None, "Generic")
        
    elif clean_choice == "Data Drift Monitoring":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            monitoring.show_monitoring(st.session_state.df)

    elif clean_choice == "Multi-Modal Analysis":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            multimodal.show_multimodal(st.session_state.df)

    elif clean_choice == "Autonomous Data Scientist":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            autonomous.run_autonomous_mode(st.session_state.df)

    elif "AI Insights" in clean_choice:
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            insights.generate_narrative_eda(st.session_state.df)

    # Removed Business Recs

    elif clean_choice == "AI Data Agent":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            llm_engine.show_llm(st.session_state.df)

    elif clean_choice == "Reporting":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            reporting.show_reporting(st.session_state.df)

    elif clean_choice == "Export & Reports":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            reporting.show_export_reporting_suite(st.session_state.df)

    elif clean_choice == "Reinforcement Learning":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            reinforcement.show_reinforcement_learning(st.session_state.df)

    elif clean_choice == "Model Interpretability":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            interpretability.show_model_interpretability(st.session_state.df)

    elif clean_choice == "Ensemble Methods":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            ensemble.show_ensemble_methods(st.session_state.df)

    elif clean_choice == "Hyperparameter Optimization":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            hyperopt.show_hyperparameter_optimization(st.session_state.df)

    elif clean_choice == "Custom Model Training":
        st.info("🚧 Custom Model Training module coming soon! This will allow training custom neural networks and advanced ML models.")

    elif clean_choice == "Transfer Learning":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            transfer_learning.show_transfer_learning(st.session_state.df)

    elif clean_choice == "Hypothesis Testing":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            hypothesis.run_hypothesis_engine(st.session_state.df)

    elif clean_choice == "A/B Testing Framework":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            statistical_testing.show_statistical_testing(st.session_state.df)

    elif clean_choice == "Causal Inference":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            statistical_testing.show_statistical_testing(st.session_state.df)

    elif clean_choice == "Bayesian Statistics":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            statistical_testing.show_statistical_testing(st.session_state.df)

    elif clean_choice == "Baseline & Significance Checks":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            statistical_testing.show_baseline_significance_checks(st.session_state.df)

    elif clean_choice == "Team Collaboration":
        collaborative.show_collaboration()

    elif clean_choice == "Text Analytics & NLP":
        if st.session_state.df is None:
            st.info("Please upload a file to proceed.")
        else:
            multimodal.show_multimodal(st.session_state.df)  # Using existing multimodal analysis which includes text analytics

    elif clean_choice == "Image Processing & CV":
        if st.session_state.df is None:
            st.info("Please upload a dataset first.")
        else:
            multimodal_advanced.show_multimodal_advanced(st.session_state.df)

    elif clean_choice == "Audio Analysis":
        if st.session_state.df is None:
            st.info("Please upload a dataset first.")
        else:
            multimodal_advanced.show_multimodal_advanced(st.session_state.df)



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error("An unexpected error occurred in the application.")
        st.error(f"Error details: {e}")
        # Optionally log detailed traceback to console for dev
        import traceback
        traceback.print_exc()
