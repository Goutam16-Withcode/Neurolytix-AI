import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Prefer the newer package `google.genai`; fall back to the deprecated module if needed.
try:
    import google.genai as genai
except Exception:
    try:
        import google.generativeai as genai
    except Exception:
        genai = None

from ui import section_header
import requests

# Load .env (if present) so environment variables are available
load_dotenv()

# Preferred environment variable names
ENV_API_KEY = "GOOGLE_GENAI_API_KEY"
ENV_MODEL = "GOOGLE_GENAI_MODEL"
ENV_OPENAI_KEY = "OPENAI_ROUTER_KEY"
ENV_OPENAI_MODEL = "OPENAI_ROUTER_MODEL"

def _attempt_client_generation(prompt, api_key, model_name=None):
    """Attempt to generate text using the standard google.genai Client.
    Returns (success, text_or_error_msg).
    """
    if genai is None:
        return False, "google.genai package not installed or failed to import."

    try:
        # Standard usage for modern google.genai
        if hasattr(genai, 'Client'):
            client = genai.Client(api_key=api_key)
            model_id = model_name or os.getenv(ENV_MODEL, 'gemini-1.5-flash')
            
            # Use the simple generate_content method
            response = client.models.generate_content(
                model=model_id,
                contents=prompt
            )
            
            if response and hasattr(response, 'text'):
                return True, response.text
            return False, "Client returned empty response or missing text."
            
        return False, "google.genai.Client not found in installed package."

    except Exception as e:
        return False, str(e)


def _attempt_legacy_generation(prompt, api_key, model_name=None):
    """Attempt to generate text using the older google.generativeai SDK.
    Returns (success, text_or_error_msg).
    """
    if genai is None:
        return False, "genai package not available"

    try:
        # Check for legacy configure method
        if hasattr(genai, 'configure'):
            genai.configure(api_key=api_key)
        
        # Check for legacy GenerativeModel
        if hasattr(genai, 'GenerativeModel'):
            name = model_name or os.getenv(ENV_MODEL) or 'gemini-1.5-flash'
            model = genai.GenerativeModel(name)
            resp = model.generate_content(prompt)
            
            # Handle response safely
            if hasattr(resp, 'text'):
                return True, resp.text
            elif hasattr(resp, 'parts'):
                 # Fallback for some response structures
                 return True, "".join([p.text for p in resp.parts])
                 
            return False, "Legacy GenerativeModel returned unparseable response."
            
        return False, "GenerativeModel interface not present in this version of genai."
    except Exception as e:
        return False, str(e)


def _attempt_openai_router_generation(prompt, api_key, model_name=None):
    """Attempt to generate text using OpenAI Router via HTTP.
    Returns (success, text_or_error_msg).
    """
    try:
        if not api_key:
            return False, "OpenAI router key not provided"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        model = model_name or os.getenv(ENV_OPENAI_MODEL) or 'gpt-4o'
        body = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 1024
        }
        url = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1/chat/completions')
        r = requests.post(url, headers=headers, json=body, timeout=30)
        if r.status_code != 200:
            return False, f"OpenAI router HTTP error {r.status_code}: {r.text}"
        j = r.json()
        # Try to extract text from Chat Completions response
        if 'choices' in j and len(j['choices']) > 0:
            ch = j['choices'][0]
            if 'message' in ch and 'content' in ch['message']:
                return True, ch['message']['content']
            if 'text' in ch:
                return True, ch['text']
        # fallback: try common keys
        if 'output' in j and isinstance(j['output'], list) and len(j['output']) > 0:
            item = j['output'][0]
            if isinstance(item, dict) and 'content' in item:
                return True, item['content']
        return False, 'OpenAI router response did not contain a recognized text output'
    except Exception as e:
        return False, str(e)


def _build_rag_context(prompt: str, df: 'pd.DataFrame', top_k: int = 3) -> str:
    """Build a retrieval-augmented context string from `df` using `offline_rag`.

    Returns a string containing the top-k retrieved passages with short source tags.
    """
    try:
        from offline_rag import build_corpus_from_df, EmbeddingIndex, FallbackIndex
    except Exception:
        # If offline_rag can't be imported, return an empty context
        return ""

    docs, keys = build_corpus_from_df(df)
    if not docs:
        return ""

    # Try embedding index first, fall back to FallbackIndex
    try:
        idx = EmbeddingIndex(docs)
    except Exception:
        idx = FallbackIndex(docs)

    results = idx.query(prompt, top_k=top_k)
    retrieved = []
    for doc_idx, score in results:
        src = keys[doc_idx] if doc_idx < len(keys) else f"doc_{doc_idx}"
        retrieved.append(f"Source: {src} (score={score:.3f})\n{docs[doc_idx]}")

    context = "\n\n".join(retrieved)
    return context


def query_llm(prompt, api_key=None, model_name=None, df_context=None, mode: str = 'offline', provider: str = None, openai_router_key: str = None):
    """High-level helper that supports Offline RAG and Remote LLM + RAG.

    Parameters
    - prompt: user prompt
    - api_key: API key for Google GenAI (optional)
    - model_name: model name to use (optional)
    - df_context: pandas DataFrame to use for retrieval
    - mode: 'offline' or 'remote'
    - provider: optional override ('openai' or 'google')
    - openai_router_key: API key for OpenAI router (optional)

    Behavior: If mode == 'offline' returns offline RAG reply. If mode == 'remote', builds RAG
    context from `df_context`, prepends it to the prompt, and attempts to call the remote LLM
    (OpenAI router preferred if key provided, else Google genai paths). On remote failure,
    falls back to offline RAG if dataset context is available.
    """
    # Offline fast path
    if mode == 'offline' or df_context is None:
        try:
            from offline_rag import offline_reply
            return offline_reply(prompt, df_context)
        except Exception as e:
            return f"Error: Offline RAG failed: {str(e)}"

    # Build RAG context from the dataframe
    rag_context = _build_rag_context(prompt, df_context, top_k=3)
    # Compose final prompt for the remote LLM
    final_prompt = ("Context (retrieved from your dataset):\n\n" + rag_context + "\n\n" +
                    "Answer the user's question concisely and cite sources from the Context (use Source: tags).\n\n" +
                    "User Question: \n" + prompt)

    # Try OpenAI router if provided / preferred
    openai_key = openai_router_key or os.getenv(ENV_OPENAI_KEY)
    if provider == 'openai' or (openai_key and (mode == 'remote')):
        try:
            ok, resp = _attempt_openai_router_generation(final_prompt, openai_key, model_name or os.getenv(ENV_OPENAI_MODEL))
            if ok:
                return resp
            last_openai_err = resp
        except Exception as e:
            last_openai_err = str(e)
    else:
        last_openai_err = None

    # Next: try Google GenAI via legacy/client paths if api_key present
    g_key = api_key or os.getenv(ENV_API_KEY)
    if g_key:
        ok, resp_legacy = _attempt_legacy_generation(final_prompt, g_key, model_name)
        if ok:
            return resp_legacy
        ok2, resp_client = _attempt_client_generation(final_prompt, g_key, model_name)
        if ok2:
            return resp_client
        last_google_err = f"legacy: {resp_legacy}; client: {resp_client}"
    else:
        last_google_err = None

    # If remote attempts failed, return offline RAG fallback (if available)
    try:
        from offline_rag import offline_reply
        return offline_reply(prompt, df_context)
    except Exception:
        # Compose detailed error for debugging
        err_parts = []
        if last_openai_err:
            err_parts.append(f"OpenAI error: {last_openai_err}")
        if last_google_err:
            err_parts.append(f"Google error: {last_google_err}")
        if err_parts:
            return "Error: Remote generation failed. " + " | ".join(err_parts)
        return "Error: Remote generation failed and offline RAG fallback also unavailable."


def show_llm(df):
    # Custom CSS for ChatGPT-like interface
    st.markdown("""
    <style>
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    }
    .chat-header {
        text-align: center;
        color: white;
        margin-bottom: 30px;
        font-size: 2.5em;
        font-weight: 300;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .chat-subtitle {
        text-align: center;
        color: rgba(255,255,255,0.8);
        margin-bottom: 20px;
        font-size: 1.1em;
    }
    .privacy-notice {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        color: white;
        font-size: 0.9em;
    }
    .settings-panel {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .chat-messages {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 15px;
        padding: 20px;
        max-height: 600px;
        overflow-y: auto;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .welcome-message {
        text-align: center;
        color: #e0e0e0;
        font-style: italic;
        margin: 40px 0;
    }
    .stChatInput {
        position: sticky;
        bottom: 0;
        background: transparent !important;
        padding: 20px;
        border-radius: 0 0 15px 15px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    # Main chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.markdown('<div class="chat-header">🤖 Neurolytix AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="chat-subtitle">Your intelligent data companion</div>', unsafe_allow_html=True)

    # Auto-detect available API keys
    openai_key_available = bool(os.getenv(ENV_OPENAI_KEY))
    google_key_available = bool(os.getenv(ENV_API_KEY))

    # Auto-select mode based on available keys
    if google_key_available or openai_key_available:
        auto_mode = "remote"
        mode_display = "☁️ Remote LLM + RAG (Cloud)"
        provider_choice = "Google Gemini" if google_key_available else "OpenAI"
    else:
        auto_mode = "offline"
        mode_display = "🔒 Offline RAG (Private)"
        provider_choice = None

    # Initialize chat history
    if "llm_messages" not in st.session_state:
        st.session_state.llm_messages = []
        # Add welcome message with mode info
        mode_info = "☁️ **Enhanced Mode** (using cloud AI)" if auto_mode == "remote" else "🔒 **Private Mode** (local processing only)"
        welcome_msg = f"""👋 **Hello! I'm your AI Data Assistant.**

{mode_info}

I can help you analyze your data, answer questions, and provide insights. What would you like to know about your dataset?"""
        st.session_state.llm_messages.append({
            "role": "assistant",
            "content": welcome_msg
        })

    # Set configuration based on auto-detection
    if auto_mode == "remote":
        if provider_choice == "OpenAI":
            user_openai_key = os.getenv(ENV_OPENAI_KEY)
            user_model = os.getenv(ENV_OPENAI_MODEL, "gpt-4o")
            user_api_key = None
        else:  # Google Gemini
            user_api_key = os.getenv(ENV_API_KEY)
            user_model = os.getenv(ENV_MODEL, "gemini-1.5-flash")
            user_openai_key = None
        mode = "☁️ Remote LLM + RAG (Cloud)"
    else:
        mode = "🔒 Offline RAG (Private)"
        provider_choice = None
        user_api_key = None
        user_openai_key = None
        user_model = None
        
    # Chat messages container
    st.markdown('<div class="chat-messages">', unsafe_allow_html=True)

    # Display chat history
    for message in st.session_state.llm_messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                # Format assistant messages with better styling
                content = message["content"].replace("**", "**").replace("*", "*")
                st.markdown(content)
            else:
                st.markdown(message["content"])

    st.markdown('</div>', unsafe_allow_html=True)

    # Chat input at the bottom
    if prompt := st.chat_input("💬 Ask me anything about your data...", key="llm_chat_input"):
        # Add user message
        st.session_state.llm_messages.append({"role": "user", "content": prompt})

        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    if mode.startswith("🔒"):
                        response = query_llm(prompt, df_context=df, mode='offline')
                    else:
                        if provider_choice == "OpenAI":
                            response = query_llm(
                                prompt,
                                api_key=None,
                                model_name=user_model,
                                df_context=df,
                                mode='remote',
                                provider='openai',
                                openai_router_key=user_openai_key
                            )
                        else:  # Google Gemini
                            response = query_llm(
                                prompt,
                                api_key=user_api_key,
                                model_name=user_model,
                                df_context=df,
                                mode='remote',
                                provider='google'
                            )

                    if isinstance(response, str) and response.startswith("Error:"):
                        st.error(f"❌ {response}")
                        response = "I encountered an error while processing your request. Please check your settings and try again."

                    st.markdown(response)
                    st.session_state.llm_messages.append({"role": "assistant", "content": response})

                except Exception as e:
                    error_msg = f"I apologize, but I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.llm_messages.append({"role": "assistant", "content": error_msg})

        # Rerun to update the chat display
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
