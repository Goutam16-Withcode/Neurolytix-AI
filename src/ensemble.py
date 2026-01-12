import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import (
    RandomForestClassifier, RandomForestRegressor,
    GradientBoostingClassifier, GradientBoostingRegressor,
    AdaBoostClassifier, AdaBoostRegressor,
    BaggingClassifier, BaggingRegressor,
    VotingClassifier, VotingRegressor,
    StackingClassifier, StackingRegressor
)
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, r2_score, classification_report, confusion_matrix
from ui import section_header
import warnings
warnings.filterwarnings('ignore')

def show_ensemble_methods(df):
    section_header("Ensemble Methods", "Combine multiple models for better performance using Bagging, Boosting, Stacking, and Voting.")

    if df is None:
        st.error("Please load a dataset first.")
        return

    # Problem setup
    target_col = st.selectbox("Select Target Column", df.columns, key="ensemble_target")
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

    # Ensemble method selection
    ensemble_methods = {
        "Bagging": "Combine multiple instances of the same model",
        "Boosting": "Sequentially improve weak learners",
        "Stacking": "Combine different models with a meta-learner",
        "Voting": "Simple majority voting for predictions"
    }

    method = st.selectbox("Select Ensemble Method", list(ensemble_methods.keys()),
                         format_func=lambda x: f"{x} - {ensemble_methods[x]}",
                         key="ensemble_method")

    # Base model selection
    if problem_type == "classification":
        base_models = {
            "Decision Tree": DecisionTreeClassifier(random_state=42),
            "Random Forest": RandomForestClassifier(n_estimators=50, random_state=42),
            "SVM": SVC(probability=True, random_state=42),
            "Naive Bayes": GaussianNB()
        }
    else:
        base_models = {
            "Decision Tree": DecisionTreeRegressor(random_state=42),
            "Random Forest": RandomForestRegressor(n_estimators=50, random_state=42),
            "Linear Regression": LinearRegression(),
            "SVM": SVR()
        }

    base_model_name = st.selectbox("Select Base Model", list(base_models.keys()), key="base_model")

    if st.button("Train Ensemble Model"):
        with st.spinner("Training ensemble model..."):
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

                # Create and train ensemble model
                ensemble_model = create_ensemble_model(method, base_models[base_model_name], problem_type)
                ensemble_model.fit(X_train, y_train)

                # Evaluate
                evaluate_ensemble_model(ensemble_model, X_train, X_test, y_train, y_test, method, problem_type)

            except Exception as e:
                st.error(f"Error training ensemble model: {str(e)}")
                st.info("Try with different parameters or check your data.")

def create_ensemble_model(method, base_model, problem_type):
    """Create the appropriate ensemble model based on method and problem type."""

    if method == "Bagging":
        if problem_type == "classification":
            return BaggingClassifier(
                base_estimator=base_model,
                n_estimators=10,
                random_state=42
            )
        else:
            return BaggingRegressor(
                base_estimator=base_model,
                n_estimators=10,
                random_state=42
            )

    elif method == "Boosting":
        if problem_type == "classification":
            if isinstance(base_model, DecisionTreeClassifier):
                return AdaBoostClassifier(
                    base_estimator=base_model,
                    n_estimators=50,
                    random_state=42
                )
            else:
                return GradientBoostingClassifier(
                    n_estimators=100,
                    random_state=42
                )
        else:
            if isinstance(base_model, DecisionTreeRegressor):
                return AdaBoostRegressor(
                    base_estimator=base_model,
                    n_estimators=50,
                    random_state=42
                )
            else:
                return GradientBoostingRegressor(
                    n_estimators=100,
                    random_state=42
                )

    elif method == "Stacking":
        # Define base estimators
        if problem_type == "classification":
            estimators = [
                ('rf', RandomForestClassifier(n_estimators=50, random_state=42)),
                ('svm', SVC(probability=True, random_state=42)),
                ('nb', GaussianNB())
            ]
            final_estimator = LogisticRegression(random_state=42)
            return StackingClassifier(estimators=estimators, final_estimator=final_estimator, cv=3)
        else:
            estimators = [
                ('rf', RandomForestRegressor(n_estimators=50, random_state=42)),
                ('lr', LinearRegression()),
                ('svm', SVR())
            ]
            final_estimator = LinearRegression()
            return StackingRegressor(estimators=estimators, final_estimator=final_estimator, cv=3)

    elif method == "Voting":
        if problem_type == "classification":
            estimators = [
                ('rf', RandomForestClassifier(n_estimators=50, random_state=42)),
                ('svm', SVC(probability=True, random_state=42)),
                ('nb', GaussianNB())
            ]
            return VotingClassifier(estimators=estimators, voting='soft')
        else:
            estimators = [
                ('rf', RandomForestRegressor(n_estimators=50, random_state=42)),
                ('lr', LinearRegression()),
                ('svm', SVR())
            ]
            return VotingRegressor(estimators=estimators)

def evaluate_ensemble_model(model, X_train, X_test, y_train, y_test, method, problem_type):
    """Evaluate the trained ensemble model."""

    st.success(f"✅ {method} ensemble model trained successfully!")

    # Predictions
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)

    # Performance metrics
    col1, col2, col3, col4 = st.columns(4)

    if problem_type == "classification":
        train_acc = accuracy_score(y_train, y_pred_train)
        test_acc = accuracy_score(y_test, y_pred_test)

        with col1:
            st.metric("Train Accuracy", f"{train_acc:.4f}")
        with col2:
            st.metric("Test Accuracy", f"{test_acc:.4f}")
        with col3:
            st.metric("Train/Test Gap", f"{abs(train_acc - test_acc):.4f}")
        with col4:
            cv_scores = cross_val_score(model, X_train, y_train, cv=5)
            st.metric("CV Score (Mean)", f"{cv_scores.mean():.4f}")

        # Classification report
        st.subheader("📊 Classification Report")
        report = classification_report(y_test, y_pred_test, output_dict=True)
        report_df = pd.DataFrame(report).transpose()
        st.dataframe(report_df.style.highlight_max(axis=0))

        # Confusion matrix
        st.subheader("🔢 Confusion Matrix")
        cm = confusion_matrix(y_test, y_pred_test)
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
        ax.set_xlabel('Predicted')
        ax.set_ylabel('Actual')
        st.pyplot(fig)

    else:  # Regression
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        train_rmse = np.sqrt(np.mean((y_train - y_pred_train)**2))
        test_rmse = np.sqrt(np.mean((y_test - y_pred_test)**2))

        with col1:
            st.metric("Train R²", f"{train_r2:.4f}")
        with col2:
            st.metric("Test R²", f"{test_r2:.4f}")
        with col3:
            st.metric("Train RMSE", f"{train_rmse:.4f}")
        with col4:
            st.metric("Test RMSE", f"{test_rmse:.4f}")

        # Predictions vs Actual plot
        st.subheader("📈 Predictions vs Actual")
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(y_test, y_pred_test, alpha=0.6)
        ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
        ax.set_xlabel('Actual Values')
        ax.set_ylabel('Predicted Values')
        ax.set_title('Ensemble Model: Predictions vs Actual')
        st.pyplot(fig)

    # Feature importance (if available)
    if hasattr(model, 'feature_importances_'):
        st.subheader("🌟 Feature Importance")
        importance_df = pd.DataFrame({
            'Feature': X_train.columns,
            'Importance': model.feature_importances_
        }).sort_values('Importance', ascending=False)

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=importance_df.head(15), x='Importance', y='Feature', ax=ax)
        ax.set_title(f'Feature Importance - {method} Ensemble')
        st.pyplot(fig)

    elif hasattr(model, 'estimators_'):
        # For ensemble methods with multiple estimators
        st.subheader("🤖 Ensemble Components")
        if hasattr(model, 'estimators_'):
            st.write(f"Number of base estimators: {len(model.estimators_)}")

            # Show individual estimator performance if possible
            if hasattr(model, 'estimators_') and len(model.estimators_) > 0:
                estimator_scores = []
                for i, estimator in enumerate(model.estimators_[:5]):  # Show first 5
                    try:
                        score = cross_val_score(estimator, X_train, y_train, cv=3).mean()
                        estimator_scores.append({
                            'Estimator': f'Base Model {i+1}',
                            'CV_Score': score
                        })
                    except:
                        continue

                if estimator_scores:
                    scores_df = pd.DataFrame(estimator_scores)
                    st.dataframe(scores_df, use_container_width=True)

    # Model details
    st.subheader("🔧 Model Configuration")
    model_info = {
        "Ensemble Method": method,
        "Problem Type": problem_type,
        "Number of Features": X_train.shape[1],
        "Training Samples": len(X_train),
        "Test Samples": len(X_test)
    }

    if hasattr(model, 'n_estimators'):
        model_info["Number of Estimators"] = model.n_estimators

    st.json(model_info)

    # Export model
    st.subheader("💾 Export Ensemble Model")
    import joblib
    import base64

    model_buffer = joblib.dumps(model)
    b64_model = base64.b64encode(model_buffer).decode()

    st.download_button(
        label="Download Ensemble Model (Joblib)",
        data=model_buffer,
        file_name=f"ensemble_{method.lower()}_model.joblib",
        mime="application/octet/stream"
    )