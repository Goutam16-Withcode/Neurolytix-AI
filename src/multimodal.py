import streamlit as st
import pandas as pd
from ui import section_header
from textblob import TextBlob
from collections import Counter

def show_multimodal(df):
    section_header("Multi-Modal Analysis", "Analyze Text and Image data.")
    
    tab1, tab2 = st.tabs(["Text Analysis", "Image Analysis"])
    
    with tab1:
        st.subheader("Text Analytics (NLP)")
        
        # Identify Object columns that might be text
        object_cols = df.select_dtypes(include=['object']).columns.tolist()
        text_col = st.selectbox("Select Text Column", object_cols)
        
        if text_col and st.button("Analyze Text"):
            # 1. Sentiment Analysis (Sample)
            st.write("### Sentiment Analysis (Sample of 10 rows)")
            sample = df[text_col].dropna().head(10).astype(str)
            
            for text in sample:
                blob = TextBlob(text)
                sentiment = blob.sentiment.polarity
                sent_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"
                st.write(f"- **{sent_label}** ({sentiment:.2f}): {text}")
                
            # 2. Word Frequency
            st.write("### Top Common Words")
            all_text = " ".join(df[text_col].dropna().astype(str).tolist())
            words = all_text.lower().split()
            word_counts = Counter(words).most_common(20)
            
            wc_df = pd.DataFrame(word_counts, columns=["Word", "Count"])
            st.bar_chart(wc_df.set_index("Word"))
            
    with tab2:
        st.subheader("Image Analytics")
        st.info("Upload an image dataset or zip file to analyze image properties (Placeholder for CV models).")
        
        img_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
        if img_file:
            st.image(img_file, caption="Uploaded Image", use_column_width=True)
            st.success("Image loaded. (Integration with CV models coming soon)")
