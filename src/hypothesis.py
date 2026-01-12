import streamlit as st
import pandas as pd
import json
import re
from ui import section_header
import stats
import llm_engine

def run_hypothesis_engine(df):
    section_header("Auto Hypothesis Generation", "Autonomous AI that formulates and tests hypotheses using offline RAG.")
    
    # No API key needed

    st.info("The AI will analyze your dataset columns, formulate scientific hypotheses, and automatically test them using statistical methods.")
    
    if st.button("Generate & Test Hypotheses"):
        with st.spinner("AI is analyzing dataset structure..."):
            # 1. Prepare Context
            columns_info = []
            for col in df.columns:
                dtype = str(df[col].dtype)
                unique_vals = df[col].nunique()
                columns_info.append(f"{col} ({dtype}, {unique_vals} unique)")
            
            prompt = f"""
            Act as a Senior Data Scientist.
            Analyze these columns: {', '.join(columns_info)}.
            
            Formulate 5 interesting hypotheses to test relationships between variables.
            Focus on potential drivers (e.g., does X affect Y?).
            
            Return ONLY a valid JSON list of objects. No markdown. No explanations.
            Format:
            [
                {{
                    "hypothesis": "There is a significant difference in Income based on Education Level",
                    "col1": "Income",
                    "col2": "Education Level",
                    "reasoning": "Standard economic theory suggests higher education correlates with income."
                }},
                ...
            ]
            """
            
            # 2. Get LLM Response (using offline RAG)
            response_text = llm_engine.query_llm(prompt, df_context=df)

            # Handle errors returned by the LLM helper
            if isinstance(response_text, str) and response_text.startswith('Error:'):
                st.error(response_text)
                return

            # 3. Parse JSON
            try:
                # Clean up markdown code blocks if present
                clean_json = response_text.replace("```json", "").replace("```", "").strip()
                hypotheses = json.loads(clean_json)

                if not isinstance(hypotheses, list):
                    st.error("AI returned invalid format.")
                    st.write(response_text)
                    return

            except Exception as e:
                st.error(f"Failed to parse AI response: {e}")
                st.write(response_text)
                return
            
            # 4. Execute Tests
            results_data = []
            
            st.subheader("Hypothesis Testing Results")
            
            for i, h in enumerate(hypotheses):
                c1 = h.get('col1')
                c2 = h.get('col2')
                statement = h.get('hypothesis')
                reason = h.get('reasoning')
                
                # Verify columns exist
                if c1 not in df.columns or c2 not in df.columns:
                    st.error(f"Skipping: Columns {c1} or {c2} not found.")
                    continue
                    
                # Run Test using stats.py
                res = stats.calculate_association(df, c1, c2)
                
                # Display Card
                status_color = "green" if res['significant'] else "grey"
                icon = "✅" if res['significant'] else "❌"
                
                with st.expander(f"{icon} Hypothesis {i+1}: {statement}", expanded=True):
                    st.markdown(f"**Reasoning:** {reason}")
                    
                    c_a, c_b, c_c = st.columns(3)
                    c_a.metric("Variables", f"{c1} vs {c2}")
                    c_b.metric("Test Used", res['test'])
                    c_c.metric("P-Value", f"{res['p_value']:.4f}")
                    
                    if res['significant']:
                        st.success(f"**ACCEPTED**: {res['message']}")
                    else:
                        st.info(f"**REJECTED**: {res['message']}")
                        
                results_data.append({
                    "Hypothesis": statement,
                    "Col 1": c1,
                    "Col 2": c2,
                    "Test": res['test'],
                    "P-Value": res['p_value'],
                    "Result": "Accepted" if res['significant'] else "Rejected"
                })
                
            # Summary Table
            if results_data:
                st.subheader("Summary Report")
                st.dataframe(pd.DataFrame(results_data))
                
            st.success("Analysis Complete.")

