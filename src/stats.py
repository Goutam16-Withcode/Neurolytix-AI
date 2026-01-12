import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, f_oneway, ttest_ind, pearsonr
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')
from ui import section_header

def detect_outliers_isolation_forest(df, contamination=0.1):
    """Detect outliers using Isolation Forest"""
    try:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return None, "No numeric columns found"

        # Prepare data
        X = df[numeric_cols].fillna(df[numeric_cols].median())
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Fit Isolation Forest
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        outlier_labels = iso_forest.fit_predict(X_scaled)

        # Get outlier scores
        scores = iso_forest.decision_function(X_scaled)

        # Create results dataframe
        results_df = df.copy()
        results_df['outlier_score'] = scores
        results_df['is_outlier'] = outlier_labels == -1

        return results_df, f"Detected {sum(outlier_labels == -1)} outliers using Isolation Forest"

    except Exception as e:
        return None, f"Isolation Forest failed: {str(e)}"

def detect_outliers_lof(df, n_neighbors=20, contamination=0.1):
    """Detect outliers using Local Outlier Factor"""
    try:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return None, "No numeric columns found"

        # Prepare data
        X = df[numeric_cols].fillna(df[numeric_cols].median())
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Fit LOF
        lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=contamination)
        outlier_labels = lof.fit_predict(X_scaled)

        # Get outlier scores (negative LOF scores)
        scores = -lof.negative_outlier_factor_

        # Create results dataframe
        results_df = df.copy()
        results_df['outlier_score'] = scores
        results_df['is_outlier'] = outlier_labels == -1

        return results_df, f"Detected {sum(outlier_labels == -1)} outliers using LOF"

    except Exception as e:
        return None, f"LOF failed: {str(e)}"

def detect_outliers_iqr(df, multiplier=1.5):
    """Detect outliers using IQR method for each numeric column"""
    try:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return None, "No numeric columns found"

        results_df = df.copy()
        outlier_counts = {}

        for col in numeric_cols:
            # Calculate IQR
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1

            # Define bounds
            lower_bound = Q1 - multiplier * IQR
            upper_bound = Q3 + multiplier * IQR

            # Detect outliers
            outliers = (df[col] < lower_bound) | (df[col] > upper_bound)
            outlier_counts[col] = outliers.sum()

            # Add column-specific outlier flag
            results_df[f'{col}_outlier'] = outliers

        # Overall outlier flag (outlier in any column)
        results_df['is_outlier'] = results_df[[f'{col}_outlier' for col in numeric_cols]].any(axis=1)

        total_outliers = results_df['is_outlier'].sum()
        return results_df, f"Detected {total_outliers} outliers using IQR method across {len(numeric_cols)} columns"

    except Exception as e:
        return None, f"IQR method failed: {str(e)}"

def analyze_data_quality(df):
    """Comprehensive data quality analysis"""
    quality_report = {
        'completeness': {},
        'uniqueness': {},
        'validity': {},
        'consistency': {}
    }

    # Completeness analysis
    for col in df.columns:
        missing_pct = df[col].isnull().sum() / len(df) * 100
        quality_report['completeness'][col] = {
            'missing_percentage': missing_pct,
            'status': 'Good' if missing_pct < 5 else 'Warning' if missing_pct < 20 else 'Critical'
        }

    # Uniqueness analysis
    for col in df.columns:
        unique_pct = df[col].nunique() / len(df) * 100
        quality_report['uniqueness'][col] = {
            'unique_percentage': unique_pct,
            'status': 'Good' if unique_pct > 1 else 'Warning' if unique_pct > 0.1 else 'Potential ID'
        }

    # Validity analysis (for numeric columns)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        # Check for infinite values
        infinite_count = np.isinf(df[col]).sum()
        # Check for negative values where they shouldn't be (heuristic)
        negative_pct = (df[col] < 0).sum() / len(df) * 100 if (df[col] < 0).any() else 0

        quality_report['validity'][col] = {
            'infinite_values': infinite_count,
            'negative_percentage': negative_pct,
            'status': 'Good' if infinite_count == 0 and negative_pct < 50 else 'Warning'
        }

    return quality_report

def show_data_quality_dashboard(df):
    """Display comprehensive data quality dashboard"""
    section_header("🔍 Advanced Data Quality & Anomaly Detection", "Comprehensive analysis of data quality and outlier detection")

    # Quality Overview
    with st.expander("📊 Data Quality Overview", expanded=True):
        quality_report = analyze_data_quality(df)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            completeness_score = sum(1 for col, data in quality_report['completeness'].items()
                                   if data['status'] == 'Good') / len(df.columns) * 100
            st.metric("Completeness", f"{completeness_score:.1f}%")

        with col2:
            uniqueness_score = sum(1 for col, data in quality_report['uniqueness'].items()
                                  if data['status'] == 'Good') / len(df.columns) * 100
            st.metric("Uniqueness", f"{uniqueness_score:.1f}%")

        with col3:
            validity_score = sum(1 for col, data in quality_report['validity'].items()
                               if data['status'] == 'Good') / len(quality_report['validity']) * 100
            st.metric("Validity", f"{validity_score:.1f}%")

        with col4:
            overall_score = (completeness_score + uniqueness_score + validity_score) / 3
            st.metric("Overall Quality", f"{overall_score:.1f}%")

    # Outlier Detection
    st.markdown("---")
    with st.expander("🔍 Outlier Detection", expanded=True):
        tab1, tab2, tab3 = st.tabs(["Isolation Forest", "Local Outlier Factor", "IQR Method"])

        with tab1:
            st.markdown("### Isolation Forest")
            contamination = st.slider("Contamination ratio", 0.01, 0.5, 0.1, key="iso_contamination")
            if st.button("Detect Outliers (Isolation Forest)", key="iso_detect"):
                with st.spinner("Running Isolation Forest..."):
                    results_df, message = detect_outliers_isolation_forest(df, contamination)
                    if results_df is not None:
                        st.success(message)

                        # Show outlier statistics
                        outlier_count = results_df['is_outlier'].sum()
                        st.metric("Outliers Detected", outlier_count)

                        # Show top outliers
                        outliers_df = results_df[results_df['is_outlier']].sort_values('outlier_score')
                        st.dataframe(outliers_df.head(10))

                        # Store results in session state
                        st.session_state.outlier_results = results_df
                    else:
                        st.error(message)

        with tab2:
            st.markdown("### Local Outlier Factor")
            n_neighbors = st.slider("Number of neighbors", 5, 50, 20, key="lof_neighbors")
            contamination_lof = st.slider("Contamination ratio", 0.01, 0.5, 0.1, key="lof_contamination")
            if st.button("Detect Outliers (LOF)", key="lof_detect"):
                with st.spinner("Running Local Outlier Factor..."):
                    results_df, message = detect_outliers_lof(df, n_neighbors, contamination_lof)
                    if results_df is not None:
                        st.success(message)

                        outlier_count = results_df['is_outlier'].sum()
                        st.metric("Outliers Detected", outlier_count)

                        outliers_df = results_df[results_df['is_outlier']].sort_values('outlier_score', ascending=False)
                        st.dataframe(outliers_df.head(10))

                        st.session_state.outlier_results = results_df
                    else:
                        st.error(message)

        with tab3:
            st.markdown("### IQR Method")
            multiplier = st.slider("IQR Multiplier", 1.0, 3.0, 1.5, key="iqr_multiplier")
            if st.button("Detect Outliers (IQR)", key="iqr_detect"):
                with st.spinner("Running IQR analysis..."):
                    results_df, message = detect_outliers_iqr(df, multiplier)
                    if results_df is not None:
                        st.success(message)

                        outlier_count = results_df['is_outlier'].sum()
                        st.metric("Outliers Detected", outlier_count)

                        # Show per-column outlier counts
                        numeric_cols = df.select_dtypes(include=[np.number]).columns
                        outlier_cols = [f'{col}_outlier' for col in numeric_cols]
                        outlier_summary = results_df[outlier_cols].sum().sort_values(ascending=False)
                        st.bar_chart(outlier_summary)

                        st.session_state.outlier_results = results_df
                    else:
                        st.error(message)

    # Outlier Actions
    if 'outlier_results' in st.session_state:
        st.markdown("---")
        with st.expander("🛠️ Outlier Actions"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button("Remove Outliers", key="remove_outliers"):
                    clean_df = st.session_state.outlier_results[~st.session_state.outlier_results['is_outlier']].drop(
                        columns=[col for col in st.session_state.outlier_results.columns if 'outlier' in col.lower()]
                    )
                    st.session_state.df = clean_df
                    st.success(f"Removed outliers. New dataset shape: {clean_df.shape}")
                    st.rerun()

            with col2:
                if st.button("Mark Outliers", key="mark_outliers"):
                    marked_df = st.session_state.outlier_results.copy()
                    marked_df['outlier_flag'] = marked_df['is_outlier'].map({True: 'OUTLIER', False: 'NORMAL'})
                    st.session_state.df = marked_df.drop(
                        columns=[col for col in marked_df.columns if col.endswith('_outlier') or col == 'is_outlier']
                    )
                    st.success("Added outlier flags to dataset")
                    st.rerun()

def analyze_utility(df):
    st.subheader("Feature Utility Analysis")
    st.write("Identifying columns that might not be useful for machine learning.")
    
    utility_data = []
    
    for col in df.columns:
        status = "Useful"
        reason = ""
        
        # 1. High Nulls
        if df[col].isnull().mean() > 0.5:
            status = "Warning"
            reason = "> 50% Missing Values"
            
        # 2. Constant Column
        elif df[col].nunique() <= 1:
            status = "Drop"
            reason = "Constant Value"
            
        # 3. High Cardinality (for object types, usually IDs)
        elif df[col].dtype == 'object' and df[col].nunique() == len(df):
            status = "Drop"
            reason = "Unique Identifier (High Cardinality)"
            
        utility_data.append({"Column": col, "Status": status, "Reason": reason})
        
    utils_df = pd.DataFrame(utility_data)
    
    # Color coding
    def color_status(val):
        color = 'green' if val == 'Useful' else 'red' if val == 'Drop' else 'orange'
        return f'color: {color}'

    st.dataframe(utils_df.style.map(color_status, subset=['Status']), width='stretch')
    
    return utils_df

def calculate_association(df, col1, col2):
    """
    Calculates statistical association between two columns based on their types.
    Returns a dictionary with test name, statistic, p-value, and conclusion.
    """
    type1 = df[col1].dtype
    type2 = df[col2].dtype
    
    is_num1 = pd.api.types.is_numeric_dtype(type1)
    is_num2 = pd.api.types.is_numeric_dtype(type2)
    
    result = {
        "test": "Unknown",
        "p_value": 1.0,
        "statistic": 0.0,
        "significant": False,
        "message": "Could not determine test."
    }
    
    try:
        # Case 1: Cat vs Cat (Chi-Square)
        if not is_num1 and not is_num2:
            contingency = pd.crosstab(df[col1], df[col2])
            if contingency.size == 0: return result
            chi2, p, dof, expected = chi2_contingency(contingency)
            result.update({
                "test": "Chi-Square Test",
                "statistic": chi2,
                "p_value": p,
                "significant": p < 0.05,
                "message": "Significant Dependency" if p < 0.05 else "Independent"
            })
                
        # Case 2: Num vs Cat (ANOVA)
        elif (is_num1 and not is_num2) or (not is_num1 and is_num2):
            num_col = col1 if is_num1 else col2
            cat_col = col2 if is_num1 else col1
            
            groups = [group[num_col].dropna().values for name, group in df.groupby(cat_col)]
            if len(groups) < 2:
                result["message"] = "Not enough groups for ANOVA"
            else:
                f_stat, p = f_oneway(*groups)
                result.update({
                    "test": "One-way ANOVA",
                    "statistic": f_stat,
                    "p_value": p,
                    "significant": p < 0.05,
                    "message": f"Significant Difference in Means" if p < 0.05 else "No Diff in Means"
                })
                    
        # Case 3: Num vs Num (Pearson)
        elif is_num1 and is_num2:
            valid_data = df[[col1, col2]].dropna()
            if len(valid_data) < 2: return result
            corr, p = pearsonr(valid_data[col1], valid_data[col2])
            result.update({
                "test": "Pearson Correlation",
                "statistic": corr,
                "p_value": p,
                "significant": p < 0.05,
                "message": "Significant Correlation" if p < 0.05 else "No Correlation"
            })
            
    except Exception as e:
        result["message"] = f"Error: {str(e)}"
        
    return result

def perform_tests(df):
    st.subheader("Statistical Hypothesis Testing")
    
    col1, col2 = st.columns(2)
    with col1:
        ft1 = st.selectbox("Select First Variable", df.columns)
    with col2:
        ft2 = st.selectbox("Select Second Variable", df.columns, index=1 if len(df.columns) > 1 else 0)
        
    if st.button("Run Significance Test"):
        res = calculate_association(df, ft1, ft2)
        
        st.info(f"Test Selected: {res['test']}")
        st.metric("P-Value", f"{res['p_value']:.4f}")
        st.metric("Statistic", f"{res['statistic']:.4f}")
        
        if res['significant']:
            st.success(f"Result: {res['message']}")
        else:
            st.warning(f"Result: {res['message']}")

def show_stats(df):
    section_header("Statistical Analysis", "Deep dive into feature utility and relationships.")
    
    tab1, tab2 = st.tabs(["Feature Utility", "Hypothesis Testing"])
    
    with tab1:
        analyze_utility(df)
        
    with tab2:
        perform_tests(df)
