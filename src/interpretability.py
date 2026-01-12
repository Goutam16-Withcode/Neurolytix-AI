import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score, r2_score
import shap
from ui import section_header
import warnings
warnings.filterwarnings('ignore')

def show_model_interpretability(df):
    section_header("Model Interpretability", "Understand and explain your machine learning models using SHAP, LIME, and feature importance analysis.")

    if df is None:
        st.error("Please load a dataset first.")
        return

    # Problem setup
    target_col = st.selectbox("Select Target Column", df.columns, key="interp_target")
    if not target_col:
        return

    # Determine problem type
    target_values = df[target_col].dropna()
    if target_values.dtype == 'object' or len(target_values.unique()) < 20:
        problem_type = "classification"
        st.info(f"🔍 Detected **{problem_type}** problem with {len(target_values.unique())} classes.")
    else:
        problem_type = "regression"
        st.info(f"🔍 Detected **{problem_type}** problem.")

    # Model selection
    if problem_type == "classification":
        models = {
            "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
            "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42)
        }
    else:
        models = {
            "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
            "Linear Regression": LinearRegression()
        }

    model_name = st.selectbox("Select Model for Interpretation", list(models.keys()), key="interp_model")

    if st.button("Train Model & Generate Interpretations"):
        with st.spinner("Training model and generating interpretations..."):
            try:
                # Prepare data
                X = df.drop(columns=[target_col]).select_dtypes(include=[np.number])
                y = df[target_col]

                if len(X.columns) == 0:
                    st.error("No numeric features found. Please preprocess your data.")
                    return

                # Handle missing values
                X = X.fillna(X.mean())
                y = y.fillna(y.mode()[0] if problem_type == "classification" else y.mean())

                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

                # Train model
                model = models[model_name]
                model.fit(X_train, y_train)

                # Evaluate model
                y_pred = model.predict(X_test)
                if problem_type == "classification":
                    accuracy = accuracy_score(y_test, y_pred)
                    st.success(f"Model trained! Test Accuracy: {accuracy:.4f}")
                else:
                    r2 = r2_score(y_test, y_pred)
                    st.success(f"Model trained! Test R² Score: {r2:.4f}")

                # Generate interpretations
                generate_interpretations(model, X_train, X_test, y_train, y_test, problem_type, model_name)

            except Exception as e:
                st.error(f"Error during model training or interpretation: {str(e)}")
                st.info("Try with a different model or check your data preprocessing.")

def generate_interpretations(model, X_train, X_test, y_train, y_test, problem_type, model_name):
    """Generate comprehensive model interpretations."""

    # Create tabs for different interpretation methods
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Feature Importance", "🔍 SHAP Analysis", "📈 Partial Dependence", "🎯 Individual Predictions"])

    with tab1:
        show_feature_importance(model, X_train, model_name)

    with tab2:
        show_shap_analysis(model, X_train, X_test, model_name)

    with tab3:
        show_partial_dependence(model, X_train, problem_type)

    with tab4:
        show_individual_predictions(model, X_test, y_test, problem_type)

def show_feature_importance(model, X_train, model_name):
    """Display feature importance analysis."""
    st.subheader("Feature Importance Analysis")

    if hasattr(model, 'feature_importances_'):
        # Tree-based models
        importance_df = pd.DataFrame({
            'Feature': X_train.columns,
            'Importance': model.feature_importances_
        }).sort_values('Importance', ascending=False)

        # Bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=importance_df.head(15), x='Importance', y='Feature', ax=ax)
        ax.set_title(f'Feature Importance - {model_name}')
        st.pyplot(fig)

        # Table
        st.dataframe(importance_df, use_container_width=True)

    elif hasattr(model, 'coef_'):
        # Linear models
        if model.coef_.ndim > 1:
            # Multi-class classification
            coef_df = pd.DataFrame(model.coef_.T, columns=[f'Class_{i}' for i in range(model.coef_.shape[0])], index=X_train.columns)
        else:
            # Binary classification or regression
            coef_df = pd.DataFrame({
                'Feature': X_train.columns,
                'Coefficient': model.coef_[0] if model.coef_.ndim > 1 else model.coef_
            }).sort_values('Coefficient', key=abs, ascending=False)

        st.dataframe(coef_df, use_container_width=True)

        # Coefficient plot
        if 'Coefficient' in coef_df.columns:
            fig, ax = plt.subplots(figsize=(10, 6))
            coef_df.head(15).plot(kind='barh', x='Feature', y='Coefficient', ax=ax)
            ax.set_title(f'Feature Coefficients - {model_name}')
            st.pyplot(fig)

    else:
        st.info("Feature importance not available for this model type.")

def show_shap_analysis(model, X_train, X_test, model_name):
    """Display SHAP (SHapley Additive exPlanations) analysis."""
    st.subheader("SHAP Analysis")

    try:
        # Create SHAP explainer
        if hasattr(model, 'predict_proba'):
            explainer = shap.TreeExplainer(model) if hasattr(model, 'feature_importances_') else shap.LinearExplainer(model, X_train)
        else:
            explainer = shap.TreeExplainer(model) if hasattr(model, 'feature_importances_') else shap.LinearExplainer(model, X_train)

        # Calculate SHAP values for a sample
        sample_size = min(100, len(X_test))
        X_sample = X_test.sample(sample_size, random_state=42)

        shap_values = explainer.shap_values(X_sample)

        # Handle different SHAP output formats
        if isinstance(shap_values, list):
            # Multi-class classification
            shap_values_to_plot = shap_values[0] if len(shap_values) > 0 else shap_values
        else:
            shap_values_to_plot = shap_values

        # Summary plot
        st.write("**SHAP Summary Plot** (shows feature impact distribution)")
        fig, ax = plt.subplots(figsize=(10, 6))
        shap.summary_plot(shap_values_to_plot, X_sample, show=False)
        st.pyplot(fig)

        # Waterfall plot for first prediction
        st.write("**SHAP Waterfall Plot** (explains single prediction)")
        fig, ax = plt.subplots(figsize=(10, 6))
        shap.plt.figure()
        shap.waterfall_plot(explainer.expected_value if not isinstance(explainer.expected_value, np.ndarray)
                          else explainer.expected_value[0],
                          shap_values_to_plot[0],
                          X_sample.iloc[0],
                          show=False)
        st.pyplot(fig)

        # Feature importance from SHAP
        st.write("**SHAP Feature Importance**")
        shap_importance = np.abs(shap_values_to_plot).mean(axis=0)
        shap_df = pd.DataFrame({
            'Feature': X_sample.columns,
            'SHAP_Importance': shap_importance
        }).sort_values('SHAP_Importance', ascending=False)

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=shap_df.head(15), x='SHAP_Importance', y='Feature', ax=ax)
        ax.set_title('SHAP Feature Importance')
        st.pyplot(fig)

    except Exception as e:
        st.error(f"SHAP analysis failed: {str(e)}")
        st.info("SHAP analysis may not be available for all model types or data configurations.")

def show_partial_dependence(model, X_train, problem_type):
    """Display partial dependence plots."""
    st.subheader("Partial Dependence Analysis")

    try:
        from sklearn.inspection import partial_dependence, PartialDependenceDisplay

        # Select features for PDP
        numeric_features = X_train.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_features) < 2:
            st.info("Need at least 2 numeric features for partial dependence analysis.")
            return

        selected_features = st.multiselect(
            "Select features for partial dependence analysis",
            numeric_features,
            default=numeric_features[:min(3, len(numeric_features))],
            key="pdp_features"
        )

        if selected_features:
            with st.spinner("Generating partial dependence plots..."):
                # Create PDP
                features = selected_features
                pd_results = partial_dependence(model, X_train, features)

                # Plot
                fig, ax = plt.subplots(figsize=(12, 8))
                PartialDependenceDisplay.from_estimator(model, X_train, features, ax=ax)
                st.pyplot(fig)

                # Explanation
                st.info("""
                **Partial Dependence Plots (PDP)** show the marginal effect of one or two features on the predicted outcome.
                - X-axis: Feature values
                - Y-axis: Predicted outcome (centered around mean)
                - The plot shows how predictions change as the feature value changes, averaging over all other features.
                """)

    except Exception as e:
        st.error(f"Partial dependence analysis failed: {str(e)}")
        st.info("Partial dependence plots may not be available for all model types.")

def show_individual_predictions(model, X_test, y_test, problem_type):
    """Show interpretation for individual predictions."""
    st.subheader("Individual Prediction Explanations")

    # Select a specific instance
    instance_idx = st.slider("Select test instance to explain", 0, len(X_test)-1, 0, key="instance_slider")

    instance = X_test.iloc[instance_idx:instance_idx+1]
    true_value = y_test.iloc[instance_idx]

    # Model prediction
    prediction = model.predict(instance)[0]
    if hasattr(model, 'predict_proba'):
        pred_proba = model.predict_proba(instance)[0]
        if problem_type == "classification":
            st.write(f"**True Value:** {true_value}")
            st.write(f"**Predicted Class:** {prediction}")
            st.write(f"**Prediction Confidence:** {pred_proba.max():.4f}")
        else:
            st.write(f"**True Value:** {true_value:.4f}")
            st.write(f"**Predicted Value:** {prediction:.4f}")
    else:
        st.write(f"**True Value:** {true_value}")
        st.write(f"**Predicted Value:** {prediction}")

    # Feature contributions (simple approach)
    st.write("**Feature Contributions** (relative to mean prediction)")

    try:
        # Calculate feature contributions using SHAP
        explainer = shap.TreeExplainer(model) if hasattr(model, 'feature_importances_') else shap.LinearExplainer(model, X_test.head(100))
        shap_values = explainer.shap_values(instance)

        if isinstance(shap_values, list):
            shap_vals = shap_values[0][0] if len(shap_values) > 0 else shap_values[0]
        else:
            shap_vals = shap_values[0]

        base_value = explainer.expected_value if not isinstance(explainer.expected_value, np.ndarray) else explainer.expected_value[0]

        contributions_df = pd.DataFrame({
            'Feature': instance.columns,
            'Value': instance.iloc[0].values,
            'SHAP_Value': shap_vals
        }).sort_values('SHAP_Value', key=abs, ascending=False)

        st.dataframe(contributions_df, use_container_width=True)

        # Waterfall-style explanation
        st.write("**Prediction Breakdown:**")
        st.write(f"Base prediction: {base_value:.4f}")
        total_shap = shap_vals.sum()
        st.write(f"Total SHAP contribution: {total_shap:.4f}")
        st.write(f"Final prediction: {base_value + total_shap:.4f}")

    except Exception as e:
        st.error(f"Individual prediction explanation failed: {str(e)}")

        # Fallback: simple feature importance
        st.write("**Fallback: Feature Values**")
        instance_df = pd.DataFrame(instance.T, columns=['Value'])
        st.dataframe(instance_df, use_container_width=True)