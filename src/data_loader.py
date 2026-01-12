import streamlit as st
import pandas as pd
import os
import zipfile
import tarfile
import tempfile
import shutil
from ui import section_header

@st.cache_data
def load_data(file):
    """
    Loads data from a generic file object (UploadedFile).
    Supports CSV, Excel, and automatically extracts compressed archives.
    """
    try:
        filename = file.name.lower()

        # Handle compressed archives
        if filename.endswith(('.zip', '.tar', '.tar.gz', '.tar.bz2', '.tar.xz', '.gz', '.bz2')):
            return load_compressed_data(file)

        # Handle regular files
        elif filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        elif filename.endswith('.json'):
            df = pd.read_json(file)
        elif filename.endswith('.parquet'):
            df = pd.read_parquet(file)
        else:
            st.warning(f"Unsupported file format: {filename}. Supported: CSV, Excel, JSON, Parquet, and compressed archives.")
            return None

        return df

    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def load_compressed_data(file):
    """
    Extracts and loads data from compressed archives.
    Supports ZIP, TAR, TAR.GZ, and other common formats.
    """
    try:
        filename = file.name.lower()

        # Create temporary directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded file to temp location
            temp_file_path = os.path.join(temp_dir, file.name)

            with open(temp_file_path, 'wb') as f:
                f.write(file.getvalue())

            # Extract based on file type
            extract_dir = os.path.join(temp_dir, 'extracted')

            if filename.endswith('.zip'):
                with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                    extracted_files = zip_ref.namelist()

            elif filename.endswith(('.tar.gz', '.tar.bz2', '.tar.xz', '.tar')):
                with tarfile.open(temp_file_path, 'r:*') as tar_ref:
                    tar_ref.extractall(extract_dir)
                    extracted_files = tar_ref.getnames()

            elif filename.endswith('.gz') and not filename.endswith('.tar.gz'):
                # Single gzipped file
                import gzip
                with gzip.open(temp_file_path, 'rb') as gz_file:
                    # Assume it's a CSV file
                    content = gz_file.read()
                    # Try to decode as CSV
                    try:
                        content_str = content.decode('utf-8')
                        from io import StringIO
                        df = pd.read_csv(StringIO(content_str))
                        st.success(f"Extracted and loaded gzipped CSV file")
                        return df
                    except:
                        st.error("Could not decode gzipped file as CSV")
                        return None

            else:
                st.error(f"Unsupported archive format: {filename}")
                return None

            # Find data files in extracted directory
            data_files = find_data_files(extract_dir)

            if not data_files:
                st.error("No supported data files found in archive (CSV, Excel, JSON, Parquet)")
                return None

            # Show extracted files
            st.success(f"📦 Extracted {len(extracted_files)} files from archive")
            with st.expander("📂 Extracted files"):
                for f in sorted(extracted_files)[:20]:  # Show first 20 files
                    st.write(f"• {f}")
                if len(extracted_files) > 20:
                    st.write(f"... and {len(extracted_files) - 20} more files")

            # Load the largest data file by default
            data_files_sorted = sorted(data_files, key=lambda x: os.path.getsize(x), reverse=True)

            if len(data_files_sorted) > 1:
                st.info(f"Found {len(data_files_sorted)} data files. Loading the largest one by default.")
                with st.expander("Available data files"):
                    for f in data_files_sorted:
                        size_mb = os.path.getsize(f) / (1024 * 1024)
                        rel_path = os.path.relpath(f, extract_dir)
                        st.write(f"• {rel_path} ({size_mb:.2f} MB)")

            target_file = data_files_sorted[0]
            file_size_mb = os.path.getsize(target_file) / (1024 * 1024)

            st.info(f"📂 Loading: {os.path.basename(target_file)} ({file_size_mb:.2f} MB)")

            # Warn about large files
            if file_size_mb > 200:
                st.warning("⚠️ Large file detected. Loading might be slow.")

            # Load based on file extension
            file_ext = os.path.splitext(target_file)[1].lower()

            if file_ext == '.csv':
                df = pd.read_csv(target_file)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(target_file)
            elif file_ext == '.json':
                df = pd.read_json(target_file)
            elif file_ext == '.parquet':
                df = pd.read_parquet(target_file)
            else:
                st.error(f"Unsupported file type in archive: {file_ext}")
                return None

            st.success(f"✅ Successfully loaded data from archive! Shape: {df.shape}")
            return df

    except Exception as e:
        st.error(f"Error extracting archive: {e}")
        return None

def find_data_files(directory):
    """
    Recursively find all supported data files in a directory.
    """
    data_files = []
    supported_exts = ['.csv', '.xlsx', '.xls', '.json', '.parquet']

    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in supported_exts):
                data_files.append(os.path.join(root, file))

    return data_files

def get_file_info(df):
    """Returns basic metadata about the dataframe."""
    info = {
        "Rows": df.shape[0],
        "Columns": df.shape[1],
        "Missing Values": df.isnull().sum().sum(),
        "Duplicate Rows": df.duplicated().sum(),
        "Memory Usage": f"{df.memory_usage(deep=True).sum() / 1024 ** 2:.2f} MB"
    }
    return info

def load_from_kaggle(handle):
    """
    Downloads dataset from Kaggle using kagglehub and loads the largest CSV found.
    """
    import kagglehub
    import glob
    import os
    
    try:
        # Download
        # Sanitize handle input
        handle = handle.strip()
        if "kagglehub.dataset_download" in handle or "kaggle.api" in handle:
             import re
             # Extract string inside quotes
             match = re.search(r'["\']([^"\']+)["\']', handle)
             if match:
                 handle = match.group(1)
        
        # Remove surrounding quotes
        handle = handle.strip('"').strip("'")

        # st.info(f"⬇️ Downloading {handle} from Kaggle Hub...")
        print(f"⬇️ Downloading {handle} from Kaggle Hub...")
        path = kagglehub.dataset_download(handle)
        # st.success(f"Downloaded to: {path}")
        print(f"Downloaded to: {path}")
        
        # Find all CSVs
        csv_files = glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)
        
        if not csv_files:
            st.error("No CSV files found in the downloaded dataset.")
            return None
            
        # Select largest CSV by default
        csv_files_sorted = sorted(csv_files, key=os.path.getsize, reverse=True)
        
        # Log available files
        if len(csv_files_sorted) > 1:
            # st.info(f"Found {len(csv_files_sorted)} CSV files. Loading the largest one by default.")
            print(f"Found {len(csv_files_sorted)} CSV files. Loading the largest one by default.")
            # with st.expander("All found files"):
            #     for f in csv_files_sorted:
            #         size_mb = os.path.getsize(f) / (1024 * 1024)
            #         st.write(f"- {os.path.basename(f)} ({size_mb:.2f} MB)")
            
        target_file = csv_files_sorted[0]
        file_size_mb = os.path.getsize(target_file) / (1024 * 1024)
        
        # st.info(f"📂 Loading file: {os.path.basename(target_file)} ({file_size_mb:.2f} MB)")
        print(f"📂 Loading file: {os.path.basename(target_file)} ({file_size_mb:.2f} MB)")
        
        # Warn if file is huge (> 200MB)
        if file_size_mb > 200:
            st.warning("⚠️ File is larger than 200MB. Loading might be slow or cause memory issues.")
        
        df = pd.read_csv(target_file)
        return df
        
    except Exception as e:
        st.error(f"Kaggle Download Failed: {e}")
        return None
