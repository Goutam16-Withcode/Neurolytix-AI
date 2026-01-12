import streamlit as st
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer, KNNImputer
from ui import section_header, clean_and_validate_data

def show_cleaning(df):
    section_header("Smart Cleaning", "Automate data preprocessing and cleaning.")
    
    st.write(f"Current Shape: {df.shape}")
    
    # Force coercion utility for messy numeric columns
    if st.button("Force Coerce Numeric Columns (aggressive) and show diagnostics"):
        df_coerced = clean_and_validate_data(df, aggressive=True)
        st.session_state.df = df_coerced
        diag = st.session_state.get('_coercion_diagnostics', {})
        if diag:
            diag_df = pd.DataFrame.from_dict(diag, orient='index').reset_index().rename(columns={'index': 'Column'})
            st.info("Coercion diagnostics computed. Review table below.")
            st.dataframe(diag_df.sort_values(by=['non_null_pct', 'unique'], ascending=[False, False]), use_container_width=True)
        else:
            st.warning("No diagnostics produced. The dataset may not have coercible formatted numbers.")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Missing Values")
        missing_count = df.isnull().sum().sum()
        st.metric("Total Missing Values", missing_count)
        
        if missing_count > 0:
            method = st.selectbox("Imputation Method", ["Drop Rows", "Mean", "Median", "Most Frequent", "KNN Imputer"])
            
            if st.button("Apply Imputation"):
                if method == "Drop Rows":
                    df_clean = df.dropna()
                elif method == "KNN Imputer":
                    # Only for numeric
                    numeric_df = df.select_dtypes(include=[np.number])
                    imputer = KNNImputer(n_neighbors=5)
                    numeric_clean = pd.DataFrame(imputer.fit_transform(numeric_df), columns=numeric_df.columns, index=numeric_df.index)
                    df_clean = df.copy()
                    df_clean[numeric_clean.columns] = numeric_clean
                    # For non-numeric, use mode
                    for col in df.select_dtypes(exclude=[np.number]).columns:
                        df_clean[col].fillna(df_clean[col].mode()[0], inplace=True)
                else:
                    # Simple Imputer logic
                    imputer_num = SimpleImputer(strategy=method.lower().replace(" ", "_"))
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if not numeric_cols.empty:
                        df[numeric_cols] = imputer_num.fit_transform(df[numeric_cols])
                    
                    # specific handling for categorical
                    cat_cols = df.select_dtypes(exclude=[np.number]).columns
                    if not cat_cols.empty:
                        imputer_cat = SimpleImputer(strategy='most_frequent')
                        df[cat_cols] = imputer_cat.fit_transform(df[cat_cols])
                    
                    df_clean = df
                
                st.session_state.df = df_clean
                st.success("Imputation Applied!")
                st.rerun()
        else:
            st.success("Data is clean of missing values.")

    with col2:
        st.subheader("Outliers")
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            target_col = st.selectbox("Select Column for Outliers", numeric_cols)
            
            # Coerce selected column to numeric for robust IQR calculation
            series = pd.to_numeric(df[target_col], errors='coerce')
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            # Identify outliers using the numeric series (ignore NaNs)
            mask_out = (series < lower_bound) | (series > upper_bound)
            outliers = df[mask_out]
            count = outliers.shape[0]

            # Show current detection and any recent removal summary
            st.metric("Outliers Detected (IQR)", count)
            if '_last_outlier_removal' in st.session_state:
                last = st.session_state['_last_outlier_removal']
                st.info(f"Last removal: {last['removed']} rows removed from '{last['col']}'")

            # Require explicit confirmation to remove
            confirm = False
            if count > 0:
                confirm = st.checkbox(f"Confirm removal of {count} outliers from '{target_col}'")

            if st.button("Remove Outliers"):
                if count == 0:
                    st.info("No outliers detected for the selected column.")
                elif not confirm:
                    st.warning("Please check the confirmation box to confirm removal.")
                else:
                    # Save a backup so user can undo
                    st.session_state._prev_df = df.copy()
                    df_clean = df.loc[~mask_out].copy()
                    st.session_state.df = df_clean
                    # Track last removal for UX clarity
                    st.session_state['_last_outlier_removal'] = {'col': target_col, 'removed': count}
                    st.success(f"Removed {count} outliers from '{target_col}'!")
                    st.rerun()

            # Allow undo if we have a previous copy
            if '_prev_df' in st.session_state:
                if st.button("Undo Remove Outliers"):
                    st.session_state.df = st.session_state._prev_df
                    del st.session_state['_prev_df']
                    # Clear last removal record when undoing
                    if '_last_outlier_removal' in st.session_state:
                        del st.session_state['_last_outlier_removal']
                    st.success("Undo complete. Restored previous dataset.")
                    st.rerun()

            # Preview of outliers
            if count > 0:
                with st.expander("Preview Removed Outliers (sample)"):
                    st.dataframe(outliers.head(10))
            else:
                st.info("No outlier rows to preview for the selected column.")

    # Add duplicate removal section
    st.subheader("Duplicate Values")
    duplicate_count = df.duplicated().sum()
    st.metric("Duplicate Rows", duplicate_count)

    if duplicate_count > 0:
        st.warning(f"Found {duplicate_count} duplicate rows in the dataset.")

        # Show duplicate details
        duplicate_rows = df[df.duplicated(keep=False)]
        with st.expander("Preview Duplicate Rows"):
            st.dataframe(duplicate_rows.head(20))

        # Option to keep first or last occurrence
        keep_option = st.radio("When removing duplicates, keep:",
                              ["First occurrence", "Last occurrence"],
                              key="duplicate_keep")

        keep = 'first' if keep_option == "First occurrence" else 'last'

        # Option to consider specific columns for duplicate detection
        subset_cols = st.multiselect("Consider only these columns for duplicate detection (leave empty for all columns):",
                                    df.columns.tolist(),
                                    key="duplicate_subset")

        subset = subset_cols if subset_cols else None

        if st.button("Remove Duplicates"):
            # Save backup for undo
            st.session_state._prev_df_duplicates = df.copy()

            # Remove duplicates
            df_clean = df.drop_duplicates(keep=keep, subset=subset)

            removed_count = len(df) - len(df_clean)
            st.session_state.df = df_clean

            # Track removal for UX
            st.session_state['_last_duplicate_removal'] = {
                'removed': removed_count,
                'keep': keep,
                'subset': subset
            }

            st.success(f"Removed {removed_count} duplicate rows!")
            st.rerun()

    else:
        st.success("No duplicate rows found in the dataset.")

    # Allow undo duplicate removal
    if '_prev_df_duplicates' in st.session_state:
        if st.button("Undo Remove Duplicates"):
            st.session_state.df = st.session_state._prev_df_duplicates
            del st.session_state._prev_df_duplicates
            # Clear last removal record when undoing
            if '_last_duplicate_removal' in st.session_state:
                del st.session_state['_last_duplicate_removal']
            st.success("Undo complete. Restored previous dataset.")
            st.rerun()

    # Show last duplicate removal summary
    if '_last_duplicate_removal' in st.session_state:
        last = st.session_state['_last_duplicate_removal']
        subset_info = f" (considering columns: {', '.join(last['subset'])})" if last['subset'] else " (all columns)"
        st.info(f"Last removal: {last['removed']} duplicate rows removed, keeping {last['keep']} occurrence{subset_info}")
