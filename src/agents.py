import streamlit as st
import time
from ui import section_header
import llm_engine

def get_agent_response(role, context, prev_messages, df):
    """
    Generates response for a specific agent role using offline RAG.
    """
    
    role_prompts = {
        "Analyst": "You are a Senior Data Analyst. Given the dataset summary, describe the most important patterns, outliers, and data quality issues. Be critical.",
        "ML Engineer": "You are a Machine Learning Engineer. Based on the Analyst's insights, recommend the best model algorithms, preprocessing steps (scaling/encoding), and feature engineering strategies.",
        "QA Agent": "You are an AI Quality Assurance Specialist. Critique the plan. Check for potential bias, overfitting risks, and data leakage. Be strict.",
        "Project Manager": "You are the Lead Data Scientist. Synthesize all previous insights into a final actionable execution plan for the user."
    }
    
    system_prompt = role_prompts.get(role, "You are a helpful AI assistant.")
    
    full_prompt = f"""
    System: {system_prompt}
    
    Context: {context}
    
    Previous Conversation:
    {prev_messages}
    
    Your Output:
    """
    
    return llm_engine.query_llm(full_prompt, df_context=df)

def run_multi_agent_system(df):
    section_header("Multi-Agent AI Team", "Watch a team of AI agents collaborate on your project using offline RAG.")
    
    # No API key needed

    # Dataset Context
    context = f"""
    Dataset Shape: {df.shape}
    Columns: {', '.join(df.columns)}
    Missing: {df.isnull().sum().sum()}
    dtypes: {df.dtypes.to_dict()}
    """
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info("The Team")
        st.markdown("""
        - 🕵️ **Analyst**: Finds patterns.
        - ⚙️ **ML Engineer**: Designs models.
        - 🛡️ **QA Agent**: Checks safety.
        - 👔 **Manager**: Summarizes.
        """)
        
        if st.button("Start AI Huddle"):
            st.session_state.agent_running = True
            st.session_state.agent_logs = []
            
    with col2:
        st.subheader("Live Collaboration")
        container = st.container()
        
        if "agent_running" in st.session_state and st.session_state.agent_running:
            conversation_history = ""
            
            # 1. Analyst
            with container:
                with st.chat_message("Analyst", avatar="🕵️"):
                    st.write("Analyzing data distribution...")
                    msg = get_agent_response("Analyst", context, conversation_history, df)
                    st.markdown(msg)
                    conversation_history += f"\nAnalyst: {msg}\n"
                    st.session_state.agent_logs.append(("Analyst", msg))
                    time.sleep(1)
            
            # 2. Engineer
            with container:
                with st.chat_message("ML Engineer", avatar="⚙️"):
                    st.write("Designing pipeline...")
                    msg = get_agent_response("ML Engineer", context, conversation_history, df)
                    st.markdown(msg)
                    conversation_history += f"\nML Engineer: {msg}\n"
                    st.session_state.agent_logs.append(("ML Engineer", msg))
                    time.sleep(1)

            # 3. QA
            with container:
                with st.chat_message("QA Agent", avatar="🛡️"):
                    st.write("Reviewing for risks...")
                    msg = get_agent_response("QA Agent", context, conversation_history, df)
                    st.markdown(msg)
                    conversation_history += f"\nQA Agent: {msg}\n"
                    st.session_state.agent_logs.append(("QA Agent", msg))
                    time.sleep(1)

            # 4. Manager
            with container:
                with st.chat_message("Project Manager", avatar="👔"):
                    st.write("Synthesizing plan...")
                    msg = get_agent_response("Project Manager", context, conversation_history, df)
                    st.markdown(msg)
                    st.session_state.agent_logs.append(("Project Manager", msg))
            
            st.session_state.agent_running = False
            st.success("Collaboration Complete!")
