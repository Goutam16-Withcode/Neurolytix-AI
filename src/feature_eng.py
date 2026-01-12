import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import PolynomialFeatures, StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
import shap
import warnings
warnings.filterwarnings('ignore')
from ui import section_header

def analyze_feature_importance(df, target_col=None):
    """Analyze feature importance using SHAP and Random Forest"""
    try:
        # Prepare data
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            return None, "No numeric columns found for analysis"

        # If no target specified, use correlation-based importance
        if target_col is None or target_col not in df.columns:
            # Calculate correlations
            corr_matrix = df[numeric_cols].corr()
            importance_dict = {}
            for col in numeric_cols:
                # Average absolute correlation with other features
                avg_corr = abs(corr_matrix[col]).mean()
                importance_dict[col] = avg_corr
            return importance_dict, "Correlation-based importance"

        # Prepare features and target
        X = df[numeric_cols].dropna()
        y = df[target_col].dropna()

        # Align indices
        common_idx = X.index.intersection(y.index)
        X = X.loc[common_idx]
        y = y.loc[common_idx]

        if len(X) < 10:
            return None, "Insufficient data for reliable analysis"

        # Train a quick model
        if y.dtype == 'object' or len(y.unique()) < 10:
            model = RandomForestClassifier(n_estimators=50, random_state=42)
        else:
            model = RandomForestRegressor(n_estimators=50, random_state=42)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model.fit(X_train, y_train)

        # Calculate SHAP values
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test)

        # Get mean absolute SHAP values
        if isinstance(shap_values, list):
            shap_values = np.abs(shap_values[0])  # For classification
        else:
            shap_values = np.abs(shap_values)

        importance_dict = {}
        for i, col in enumerate(X.columns):
            importance_dict[col] = np.mean(shap_values[:, i])

        return importance_dict, "SHAP-based feature importance"

    except Exception as e:
        return None, f"Analysis failed: {str(e)}"

def get_smart_suggestions(df):
    """Generate smart feature engineering suggestions based on data analysis"""
    suggestions = []

    # Analyze data types
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    datetime_cols = []

    # Check for potential datetime columns
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                pd.to_datetime(df[col].dropna().iloc[:5], errors='coerce')
                datetime_cols.append(col)
            except:
                pass

    # Skewness analysis
    if numeric_cols:
        skewness = df[numeric_cols].skew()
        highly_skewed = skewness[abs(skewness) > 1].index.tolist()
        if highly_skewed:
            suggestions.append(f"🔄 **Transform skewed features**: {', '.join(highly_skewed[:3])} - Consider log or sqrt transformations")

    # Missing values
    missing_pct = (df.isnull().sum() / len(df)) * 100
    high_missing = missing_pct[missing_pct > 20].index.tolist()
    if high_missing:
        suggestions.append(f"🧹 **Handle missing values**: {', '.join(high_missing[:3])} have >20% missing data")

    # Categorical features
    if categorical_cols:
        cat_cardinality = df[categorical_cols].nunique()
        high_card = cat_cardinality[cat_cardinality > 10].index.tolist()
        if high_card:
            suggestions.append(f"🏷️ **High cardinality categoricals**: {', '.join(high_card[:3])} - Consider target encoding")

    # Date features
    if datetime_cols:
        suggestions.append(f"📅 **Extract date features** from: {', '.join(datetime_cols[:3])} (year, month, day, weekday)")

    # Correlation analysis
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()
        high_corr = []
        for i in range(len(numeric_cols)):
            for j in range(i+1, len(numeric_cols)):
                if abs(corr_matrix.iloc[i, j]) > 0.8:
                    high_corr.append(f"{numeric_cols[i]}↔{numeric_cols[j]}")
        if high_corr[:2]:  # Show only first 2
            suggestions.append(f"🔗 **Highly correlated pairs**: {', '.join(high_corr[:2])} - Consider feature selection")

    # Default suggestions if none found
    if not suggestions:
        suggestions = [
            "✅ **Data looks clean** - Consider polynomial features for non-linear relationships",
            "📊 **Add interaction features** - Multiply related numeric columns",
            "⚖️ **Scale features** if using distance-based algorithms (KNN, SVM)"
        ]

    return suggestions

def generate_features(df):
    section_header("Auto Feature Engineering", "Transform your data to boost model performance.")
    
    st.markdown(f"**Current Dataset Shape:** `{df.shape}`")
    
    with st.expander("Feature Engineering Tips"):
        st.info("""
        - **Log Transform**: Good for skewed data (e.g., Prices, Income).
        - **Scaling**: Essential for KNN, SVM, Neural Networks.
        - **Encoding**: Convert text to numbers for ML models.
        - **Polynomials**: Captures non-linear relationships.
        """)

    # AI-Powered Feature Engineering Assistant
    with st.expander("🤖 AI Feature Engineering Assistant", expanded=True):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### Smart Recommendations")
            suggestions = get_smart_suggestions(df)
            for suggestion in suggestions:
                st.markdown(f"- {suggestion}")

        with col2:
            st.markdown("### Feature Importance")
            target_col = st.selectbox("Target column (optional)", ["None"] + df.columns.tolist(), key="importance_target")
            if st.button("Analyze Feature Importance", key="analyze_importance"):
                with st.spinner("Analyzing features..."):
                    target = None if target_col == "None" else target_col
                    importance_dict, method = analyze_feature_importance(df, target)

                    if importance_dict:
                        st.markdown(f"**Method:** {method}")
                        # Sort by importance
                        sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)

                        # Display top 10
                        for feature, importance in sorted_features[:10]:
                            st.progress(min(importance, 1.0), text=f"{feature}: {importance:.3f}")
                    else:
                        st.warning(method)

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📅 Date Extraction", "🔢 Transformations", "📏 Scaling", "🔠 Encoding", "❌ Interaction/Poly"])
    
    # -------------------------
    # TAB 1: DATE EXTRACTION
    # -------------------------
    with tab1:
        date_cols = df.select_dtypes(include=['datetime64', 'object']).columns
        potential_dates = []
        for col in date_cols:
            try:
                # Quick check if first non-null looks like date
                first_valid = df[col].dropna().iloc[0]
                pd.to_datetime(first_valid)
                potential_dates.append(col)
            except:
                pass
                
        if potential_dates:
            st.write("### Date-Based Features")
            selected_date_col = st.selectbox("Select Date Column", potential_dates)
            
            if st.button("Extract Date Features"):
                try:
                    df[selected_date_col] = pd.to_datetime(df[selected_date_col], errors='coerce')
                    df[f'{selected_date_col}_year'] = df[selected_date_col].dt.year
                    df[f'{selected_date_col}_month'] = df[selected_date_col].dt.month
                    df[f'{selected_date_col}_day'] = df[selected_date_col].dt.day
                    df[f'{selected_date_col}_dow'] = df[selected_date_col].dt.dayofweek
                    
                    st.session_state.df = df
                    st.success(f"Extracted Year, Month, Day, DOW from {selected_date_col}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to convert: {e}")
        else:
            st.info("No date columns detected.")

    # -------------------------
    # TAB 2: TRANSFORMATIONS
    # -------------------------
    with tab2:
        st.write("### Review Skewness & Transform")
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        col_trans = st.selectbox("Select Column to Transform", numeric_cols)
        if col_trans:
            transform = st.radio("Transformation Type", ["Log (Natural)", "Square Root", "Box-Cox (Approx)"])
            
            if st.button("Apply Transformation"):
                try:
                    if transform == "Log (Natural)":
                        # Handle zeros/negatives by adding offset
                        if (df[col_trans] <= 0).any():
                            offset = abs(df[col_trans].min()) + 1
                            df[f'{col_trans}_log'] = np.log(df[col_trans] + offset)
                            msg = f"Applied Log Transform (with offset {offset})"
                        else:
                            df[f'{col_trans}_log'] = np.log(df[col_trans])
                            msg = "Applied Log Transform"
                            
                    elif transform == "Square Root":
                        if (df[col_trans] < 0).any():
                            st.error("Cannot apply Sqrt to negative values.")
                        else:
                            df[f'{col_trans}_sqrt'] = np.sqrt(df[col_trans])
                            msg = "Applied Square Root Transform"
                            
                    st.session_state.df = df
                    st.success(msg)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    # -------------------------
    # TAB 3: SCALING
    # -------------------------
    with tab3:
        st.write("### Standardize or Normalize")
        cols_to_scale = st.multiselect("Select Columns to Scale", numeric_cols)
        method = st.radio("Scaling Method", ["Standard Scaler (Z-Score)", "MinMax Scaler (0-1)"])
        
        if st.button("Apply Scaling"):
            if not cols_to_scale:
                st.warning("Select columns first.")
            else:
                if "Standard" in method:
                    scaler = StandardScaler()
                    df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])
                else:
                    scaler = MinMaxScaler()
                    df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])
                    
                st.session_state.df = df
                st.success(f"Scaled {len(cols_to_scale)} columns using {method}")
                st.rerun()

    # -------------------------
    # TAB 4: ENCODING
    # -------------------------
    with tab4:
        st.write("### Categorical Encoding")
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if cat_cols:
            enc_col = st.selectbox("Select Categorical Column", cat_cols)
            enc_method = st.radio("Encoding Method", ["Label Encoding", "One-Hot Encoding"])
            
            if st.button("Apply Encoding"):
                if enc_method == "Label Encoding":
                    le = LabelEncoder()
                    df[enc_col] = le.fit_transform(df[enc_col].astype(str))
                    st.success(f"Label Encoded {enc_col}")
                else:
                    dummies = pd.get_dummies(df[enc_col], prefix=enc_col)
                    df = pd.concat([df, dummies], axis=1)
                    df.drop(columns=[enc_col], inplace=True)
                    st.success(f"One-Hot Encoded {enc_col} ({dummies.shape[1]} new cols)")
                    
                st.session_state.df = df
                st.rerun()
        else:
            st.info("No categorical columns found.")

    # -------------------------
    # TAB 5: POLY/INTERACTION
    # -------------------------
    with tab5:
        st.write("### Polynomials & Interactions")
        
        # Polynomials
        if st.checkbox("Generate Polynomial Features"):
            poly_cols = st.multiselect("Columns for Polynomials", numeric_cols, key='poly_select')
            degree = st.slider("Degree", 2, 3, 2)
            if st.button("Generate Polynomials", key='btn_poly'):
                poly = PolynomialFeatures(degree=degree, include_bias=False)
                poly_data = poly.fit_transform(df[poly_cols])
                names = poly.get_feature_names_out(poly_cols)
                
                # Create DF
                temp_df = pd.DataFrame(poly_data, columns=names, index=df.index)
                # Keep only new columns
                new = [c for c in temp_df.columns if c not in df.columns]
                df = pd.concat([df, temp_df[new]], axis=1)
                
                st.session_state.df = df
                st.success(f"Added {len(new)} polynomial features.")
                st.rerun()

        st.markdown("---")
        
        # Interactions
        st.write("**Manual Interaction**")
        if len(numeric_cols) >= 2:
            c1, c2, c3 = st.columns(3)
            col_a = c1.selectbox("Col A", numeric_cols, key='int_a')
            col_b = c2.selectbox("Col B", numeric_cols, index=1, key='int_b')
            op = c3.selectbox("Op", ["*", "/", "+", "-"], key='int_op')
            
            if st.button("Create Interaction", key='btn_int'):
                name = f"{col_a}_{op}_{col_b}"
                if op == "*": df[name] = df[col_a] * df[col_b]
                elif op == "/": df[name] = df[col_a] / (df[col_b] + 1e-9)
                elif op == "+": df[name] = df[col_a] + df[col_b]
                elif op == "-": df[name] = df[col_a] - df[col_b]
                
                st.session_state.df = df
                st.success(f"Created {name}")
                st.rerun()
