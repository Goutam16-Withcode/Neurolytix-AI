import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import ks_2samp
from ui import section_header, apply_neuro_theme

def show_monitoring(current_df):
    section_header("Data Drift Monitoring", "Detect shifts between training (reference) and current data.")
    
    st.info("Upload a Reference Dataset (e.g., the data you used for training) to compare against the current loaded data.")
    
    ref_file = st.file_uploader("Upload Reference Data (CSV)", type=['csv'])
    
    if ref_file:
        try:
            ref_df = pd.read_csv(ref_file)
            st.success(f"Reference Data Loaded: {ref_df.shape[0]} rows")
            
            # Common Columns
            common_cols = list(set(current_df.columns) & set(ref_df.columns))
            numeric_cols = [c for c in common_cols if pd.api.types.is_numeric_dtype(current_df[c])]
            
            if not numeric_cols:
                st.warning("No common numeric columns found to check for drift.")
                return
                
            drift_report = []
            
            st.subheader("Drift Analysis (KS-Test)")
            
            for col in numeric_cols:
                # KS Test returns statistic and p-value
                # Null hypothesis: derived from same distribution
                # Low p-value (< 0.05) -> Drift Detected
                stat, p_val = ks_2samp(ref_df[col].dropna(), current_df[col].dropna())
                
                drift_detected = "YES" if p_val < 0.05 else "NO"
                drift_report.append({
                    "Feature": col,
                    "P-Value": f"{p_val:.4f}",
                    "Drift Detected": drift_detected,
                    "KS Stat": f"{stat:.4f}"
                })
                
            drift_df = pd.DataFrame(drift_report)
            
            # Styling
            def highlight_drift(val):
                color = 'red' if val == "YES" else 'green'
                return f'color: {color}; font-weight: bold'

            st.dataframe(drift_df.style.map(highlight_drift, subset=['Drift Detected']), use_container_width=True)
            
            # Visual Comparison
            st.subheader("Distribution Comparison")
            selected_col = st.selectbox("Select Feature to Visualize", numeric_cols)
            
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=ref_df[selected_col], name='Reference', opacity=0.5))
            fig.add_trace(go.Histogram(x=current_df[selected_col], name='Current', opacity=0.5))
            fig.update_layout(barmode='overlay', title=f"Distribution Shift: {selected_col}")
            st.plotly_chart(apply_neuro_theme(fig), use_container_width=True, theme=None)
            
        except Exception as e:
            st.error(f"Error processing reference file: {e}")
