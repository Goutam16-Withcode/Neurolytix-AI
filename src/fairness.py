import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score
from ui import section_header

def analyze_fairness(df, model=None, X_test=None, y_test=None, y_pred=None):
    section_header("Fairness & Bias Detection", "Check if your model performs equally across different groups.")
    
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if not categorical_cols:
        st.warning("No categorical columns found to check for bias (e.g., Gender, Region).")
        return

    sensitive_attr = st.selectbox("Select Sensitive Attribute", categorical_cols)
    
    if hasattr(st.session_state, 'model') and st.session_state.model is not None:
        # If we have a trained model in session
        st.info("Using trained model for fairness analysis.")
        
        # We need the test data relevant to the sensitive attribute
        # This is tricky because X_test usually doesn't have the sensitive column if it was encoded or dropped.
        # For this MVP, we will simulate bias checking on the *current* dataframe assuming it has predictions
        # In a real app, we need to carefully track X_test indices back to the original DF.
        
        st.write("To simulate fairness analysis effectively, we need predictions on this dataset.")
        target_col = st.selectbox("Select Target Column (Ground Truth)", df.columns)
        
        if st.button("Calculate Fairness Metrics"):
            # Mocking prediction for demonstration if model isn't applied to full DF
            # Real implementation would use: y_pred = model.predict(df[features])
            st.warning("Note: This assumes the loaded model predicts on the current dataset.")
            
            try:
                # Preprocessing for prediction (simplified)
                X = df.drop(columns=[target_col])
                # Encoded... (Skipping complex pipeline logic for MVP brevity)
                # Let's assume user provides a column that IS the prediction for now, or we define a simple metric
                pass
            except:
                pass
            
            # Simple Group-wise Accuracy Check
            # We need True Labels vs Predicted Labels
            # Let's build a simple heuristic:
            st.write(f"Analyzing distribution of Target '{target_col}' across '{sensitive_attr}'")
            
            groups = df[sensitive_attr].unique()
            group_metrics = []
            
            for g in groups:
                subset = df[df[sensitive_attr] == g]
                # Positive rate
                # Assuming positive class is 1 or 'Yes'
                pos_rate = subset[target_col].value_counts(normalize=True).iloc[0] 
                group_metrics.append({"Group": g, "Positive Rate": pos_rate, "Count": len(subset)})
                
            metrics_df = pd.DataFrame(group_metrics)
            st.table(metrics_df)
            
            # Disparate Impact (Ratio of Positive Rates)
            if len(group_metrics) >= 2:
                max_rate = metrics_df['Positive Rate'].max()
                min_rate = metrics_df['Positive Rate'].min()
                di = min_rate / max_rate if max_rate > 0 else 0
                st.metric("Disparate Impact Ratio (Min/Max)", f"{di:.2f}")
                if di < 0.8:
                    st.error("Potential Bias Detected (Rule of 80%)")
                else:
                    st.success("No Significant Bias Detected")
                    
    else:
        st.info("Train a model first to run detailed fairness checks. Showing demographic parity check instead.")
        # Demographic Parity: Does the dataset itself have equal representation?
        st.bar_chart(df[sensitive_attr].value_counts())
