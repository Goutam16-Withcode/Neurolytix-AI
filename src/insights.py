import streamlit as st
import pandas as pd
from ui import section_header
import llm_engine

import os

def generate_narrative_eda(df):
    """Generates a text-based summary of the dataset functionality."""
    # No API key needed

    section_header("AI-Powered Narrative EDA", "Let the AI explain your dataset to you using offline RAG.")
    
    if st.button("📝 Generate Narrative Report"):
        with st.spinner("Analyzing dataset structure and statistics..."):
            # Create a compact summary to fit in context window
            summary = df.describe().to_string()
            dtypes = df.dtypes.to_string()
            missing = df.isnull().sum().to_string()
            
            prompt = f"""
            Act as a Lead Data Analyst. Write a comprehensive 'Narrative EDA' report for this dataset.
            
            Dataset Statistics:
            {summary}
            
            Data Types:
            {dtypes}
            
            Missing Values:
            {missing}
            
            Structure your response as follows:
            1. **Executive Summary**: High-level overview.
            2. **Key Patterns**: Notable distributions, skewness, or potential outliers (deduced from stats).
            3. **Data Quality**: Comment on missingness and types.
            4. **Next Steps**: What should be analyzed next?
            """
            
            # Using offline RAG
            response = llm_engine.query_llm(prompt, df_context=df)
            if isinstance(response, str) and response.startswith('Error:'):
                st.error(response)
            else:
                st.markdown(response)

def generate_business_recommendations(df):
    """Generates strategic business advice based on data context."""
    # No API key needed

    section_header("Business Recommendation Engine", "Convert data insights into actionable business strategy using offline RAG.")
    
    target_col = st.selectbox("Select Target / Key KPI (e.g., Sales, Churn, Profit)", df.columns)
    
    if st.button("💡 Get Strategic Advice"):
        with st.spinner("Consulting the AI Strategy Team..."):
            # Correlation analysis for context
            corr_context = ""
            numeric_df = df.select_dtypes(include=['number'])
            if target_col in numeric_df.columns:
                corrs = numeric_df.corr()[target_col].sort_values(ascending=False).head(5)
                corr_context = f"Top Correlations with {target_col}:\n{corrs.to_string()}"
            
            prompt = f"""
            Act as a Top-Tier Management Consultant (McKinsey/BCG style).
            The user is analyzing a dataset with a key focus on: '{target_col}'.
            
            Context - {corr_context}
            
            Columns available: {', '.join(df.columns)}
            
            Provide 3-5 Actionable Strategic Recommendations to improve '{target_col}'.
            For each recommendation:
            - **Strategy**: What to do.
            - **Rationale**: Why (based on potential data drivers).
            - **Expected Impact**: High/Medium/Low.
            """
            
            # Using offline RAG
            response = llm_engine.query_llm(prompt, df_context=df)
            if isinstance(response, str) and response.startswith('Error:'):
                st.error(response)
            else:
                st.markdown(response)
