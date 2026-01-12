import streamlit as st
import os
import zipfile
import io
from ui import section_header

def generate_deployment_package(model, model_type):
    section_header("Model Deployment", "Deploy your model to production.")
    
    st.markdown("""
    ### 📦 Export Options
    1. **Download Model**: Get the `.pkl` file.
    2. **Generate API**: Get a FastAPI code snippet to serve this model.
    """)
    
    # Retrieve model from session if not directly passed
    if model is None and 'model' in st.session_state:
        model = st.session_state['model']
        
    if model is None:
        st.warning("No trained model found. Please train a model in 'AutoML' or 'Autonomous Mode' first.")
    else:
        st.success(f"Model ready for deployment: {type(model).__name__}")
        
        # 1. Download Pickle
        buffer = io.BytesIO()
        import joblib
        joblib.dump(model, buffer)
        
        st.download_button(
            label="Download Model (.pkl)",
            data=buffer.getvalue(),
            file_name="neurolytix_model.pkl",
            mime="application/octet-stream"
        )
        
    # 2. Generate API Code
    st.subheader("FastAPI Code Generator")
    
    api_code = f"""
from fastapi import FastAPI
import joblib
import pandas as pd
from pydantic import BaseModel

app = FastAPI()

# Load Model
model = joblib.load("model.pkl")

class InputData(BaseModel):
    # Define your fields here based on training data
    # Example:
    # feature1: float
    # feature2: str
    pass

@app.post("/predict")
def predict(data: InputData):
    df = pd.DataFrame([data.dict()])
    prediction = model.predict(df)
    return {{"prediction": prediction[0].tolist()}}

# Run with: uvicorn main:app --reload
    """
    
    st.code(api_code, language='python')
    
    if st.button("Download API Project (Zip)"):
        # Create a zip in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            zip_file.writestr("main.py", api_code)
            zip_file.writestr("requirements.txt", "fastapi\nuvicorn\njoblib\npandas\nscikit-learn")
            
        st.download_button(
            label="Download API Zip",
            data=zip_buffer.getvalue(),
            file_name="deployment_package.zip",
            mime="application/zip"
        )
