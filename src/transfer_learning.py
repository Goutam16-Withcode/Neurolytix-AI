import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC, SVR
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, r2_score, classification_report
from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin
import joblib
from ui import section_header
import warnings
warnings.filterwarnings('ignore')

class TransferLearner(BaseEstimator):
    """A simple transfer learning implementation using knowledge transfer between models."""

    def __init__(self, base_model=None, transfer_method='feature_transfer'):
        self.base_model = base_model
        self.transfer_method = transfer_method
        self.source_model = None
        self.feature_importance_transfer = None
        self.scaler = StandardScaler()

    def fit_source(self, X_source, y_source):
        """Fit the source model on source domain data."""
        if self.base_model is None:
            # Auto-select model based on target type
            if len(np.unique(y_source)) > 10:  # Regression
                self.base_model = RandomForestRegressor(n_estimators=100, random_state=42)
            else:  # Classification
                self.base_model = RandomForestClassifier(n_estimators=100, random_state=42)

        # Scale features
        X_source_scaled = self.scaler.fit_transform(X_source)

        # Train source model
        self.source_model = self.base_model.__class__(**self.base_model.get_params())
        self.source_model.fit(X_source_scaled, y_source)

        # Store feature importance for transfer
        if hasattr(self.source_model, 'feature_importances_'):
            self.feature_importance_transfer = self.source_model.feature_importances_

        return self

    def transfer_to_target(self, X_target, y_target, transfer_strength=0.5):
        """Transfer knowledge to target domain and fine-tune."""

        # Scale target features using source scaler
        X_target_scaled = self.scaler.transform(X_target)

        if self.transfer_method == 'feature_transfer' and self.feature_importance_transfer is not None:
            # Feature importance transfer: weight features based on source importance
            feature_weights = self.feature_importance_transfer ** transfer_strength
            X_target_weighted = X_target_scaled * feature_weights
        else:
            X_target_weighted = X_target_scaled

        # Fine-tune on target data
        target_model = self.base_model.__class__(**self.base_model.get_params())
        target_model.fit(X_target_weighted, y_target)

        return target_model

def generate_synthetic_source_data(n_samples=1000, n_features=10, problem_type='classification'):
    """Generate synthetic source domain data for transfer learning demonstration."""
    np.random.seed(42)

    # Generate base features
    X = np.random.randn(n_samples, n_features)

    if problem_type == 'classification':
        # Create some informative features
        y = ((X[:, 0] + X[:, 1]) > 0).astype(int)  # Linear combination
        # Add noise
        noise_idx = np.random.choice(n_samples, size=int(0.1 * n_samples), replace=False)
        y[noise_idx] = 1 - y[noise_idx]
    else:  # regression
        y = X[:, 0] * 2 + X[:, 1] * -1 + np.random.randn(n_samples) * 0.1

    return pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)]), pd.Series(y, name='target')

def show_transfer_learning(df):
    section_header("Transfer Learning", "Transfer knowledge from source domains to improve learning on target tasks.")

    if df is None:
        st.error("Please load a dataset first.")
        return

    # Transfer learning setup
    st.subheader("Transfer Learning Setup")

    # Problem type detection
    target_col = st.selectbox("Select Target Column", df.columns, key="tl_target")
    if not target_col:
        return

    target_values = df[target_col].dropna()
    if target_values.dtype == 'object' or len(target_values.unique()) < 20:
        problem_type = "classification"
        st.info(f"🔍 Detected **{problem_type}** problem with {len(target_values.unique())} classes.")
    else:
        problem_type = "regression"
        st.info(f"🔍 Detected **{problem_type}** problem.")

    # Source domain selection
    source_options = ["Generate Synthetic Source Data", "Use Subset of Current Data"]
    source_choice = st.selectbox("Source Domain", source_options, key="source_choice")

    # Transfer method
    transfer_methods = {
        "Feature Transfer": "Transfer feature importance knowledge from source to target",
        "Model Fine-tuning": "Use pre-trained model and fine-tune on target data",
        "Domain Adaptation": "Adapt model to work better on target distribution"
    }

    transfer_method = st.selectbox("Transfer Method",
                                 list(transfer_methods.keys()),
                                 format_func=lambda x: f"{x} - {transfer_methods[x]}",
                                 key="transfer_method")

    # Parameters
    col1, col2 = st.columns(2)
    with col1:
        transfer_strength = st.slider("Transfer Strength", 0.0, 1.0, 0.5,
                                    help="How much knowledge to transfer (0=no transfer, 1=full transfer)")
    with col2:
        test_size = st.slider("Test Size", 0.1, 0.5, 0.2)

    if st.button("Perform Transfer Learning"):
        with st.spinner("Performing transfer learning..."):
            try:
                # Prepare target data
                X_target = df.drop(columns=[target_col]).select_dtypes(include=[np.number])
                y_target = df[target_col]

                if len(X_target.columns) == 0:
                    st.error("No numeric features found in target data.")
                    return

                # Handle missing values
                X_target = X_target.fillna(X_target.mean())
                if y_target.dtype == 'object':
                    le = LabelEncoder()
                    y_target = le.fit_transform(y_target)

                X_train, X_test, y_train, y_test = train_test_split(
                    X_target, y_target, test_size=test_size, random_state=42
                )

                # Prepare source data
                if source_choice == "Generate Synthetic Source Data":
                    X_source, y_source = generate_synthetic_source_data(
                        n_samples=len(X_train), n_features=len(X_train.columns), problem_type=problem_type
                    )
                    # Make source data have similar feature names
                    X_source.columns = X_train.columns
                else:
                    # Use a subset of target data as source (simulating related domain)
                    source_size = min(len(X_train) // 2, 500)
                    source_indices = np.random.choice(len(X_train), source_size, replace=False)
                    X_source = X_train.iloc[source_indices]
                    y_source = y_train[source_indices]

                # Initialize transfer learner
                transfer_learner = TransferLearner(transfer_method=transfer_method.lower().replace(' ', '_'))

                # Train source model
                transfer_learner.fit_source(X_source, y_source)

                # Transfer to target
                target_model = transfer_learner.transfer_to_target(X_train, y_train, transfer_strength)

                # Evaluate
                results = evaluate_transfer_learning(
                    transfer_learner.source_model, target_model, X_source, X_test, y_source, y_test, problem_type
                )

                # Display results
                display_transfer_results(results, transfer_method, problem_type)

            except Exception as e:
                st.error(f"Transfer learning failed: {str(e)}")
                st.info("Try with different parameters or check your data preprocessing.")

def evaluate_transfer_learning(source_model, target_model, X_source, X_test, y_source, y_test, problem_type):
    """Evaluate transfer learning performance."""

    # Predictions
    y_source_pred = source_model.predict(X_source)
    y_test_pred = target_model.predict(X_test)

    results = {}

    if problem_type == "classification":
        # Source domain performance
        source_acc = accuracy_score(y_source, y_source_pred)

        # Target domain performance
        target_acc = accuracy_score(y_test, y_test_pred)

        # Baseline: train model only on target data
        if problem_type == "classification":
            baseline_model = RandomForestClassifier(n_estimators=100, random_state=42)
        else:
            baseline_model = RandomForestRegressor(n_estimators=100, random_state=42)

        baseline_model.fit(X_source.sample(frac=0.1, random_state=42), y_source.sample(frac=0.1, random_state=42))  # Small sample
        baseline_model.fit(X_test.sample(frac=0.5, random_state=42) if len(X_test) > 10 else X_test,
                          y_test[:len(X_test)//2] if len(X_test) > 10 else y_test)
        y_baseline_pred = baseline_model.predict(X_test)
        baseline_acc = accuracy_score(y_test, y_baseline_pred)

        results = {
            'source_accuracy': source_acc,
            'target_accuracy': target_acc,
            'baseline_accuracy': baseline_acc,
            'transfer_gain': target_acc - baseline_acc,
            'source_predictions': y_source_pred,
            'target_predictions': y_test_pred,
            'baseline_predictions': y_baseline_pred,
            'true_labels': y_test
        }

    else:  # Regression
        source_r2 = r2_score(y_source, y_source_pred)
        target_r2 = r2_score(y_test, y_test_pred)

        # Simple baseline
        baseline_pred = np.mean(y_train) if 'y_train' in locals() else np.mean(y_source)
        baseline_r2 = r2_score(y_test, [baseline_pred] * len(y_test))

        results = {
            'source_r2': source_r2,
            'target_r2': target_r2,
            'baseline_r2': baseline_r2,
            'transfer_gain': target_r2 - baseline_r2,
            'source_predictions': y_source_pred,
            'target_predictions': y_test_pred,
            'baseline_predictions': [baseline_pred] * len(y_test),
            'true_labels': y_test
        }

    return results

def display_transfer_results(results, transfer_method, problem_type):
    """Display transfer learning results."""

    st.success("Transfer learning completed!")

    # Performance metrics
    st.subheader("📊 Performance Comparison")

    if problem_type == "classification":
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Source Domain Accuracy", f"{results['source_accuracy']:.3f}")
        with col2:
            st.metric("Target Domain Accuracy", f"{results['target_accuracy']:.3f}")
        with col3:
            st.metric("Baseline Accuracy", f"{results['baseline_accuracy']:.3f}")
        with col4:
            st.metric("Transfer Gain", f"{results['transfer_gain']:+.3f}")

    else:  # Regression
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Source Domain R²", f"{results['source_r2']:.3f}")
        with col2:
            st.metric("Target Domain R²", f"{results['target_r2']:.3f}")
        with col3:
            st.metric("Baseline R²", f"{results['baseline_r2']:.3f}")
        with col4:
            st.metric("Transfer Gain", f"{results['transfer_gain']:+.3f}")

    # Performance visualization
    st.subheader("📈 Performance Visualization")

    if problem_type == "classification":
        accuracies = [results['baseline_accuracy'], results['target_accuracy']]
        labels = ['Baseline (No Transfer)', 'Transfer Learning']
    else:
        accuracies = [results['baseline_r2'], results['target_r2']]
        labels = ['Baseline (No Transfer)', 'Transfer Learning']

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, accuracies, color=['lightcoral', 'lightgreen'])
    ax.set_ylabel('Accuracy' if problem_type == 'classification' else 'R² Score')
    ax.set_title(f'{transfer_method} Performance Comparison')
    ax.bar_label(bars, fmt='.3f')

    # Add reference line
    if problem_type == "classification":
        ax.axhline(y=results['source_accuracy'], color='blue', linestyle='--', alpha=0.7, label='Source Domain')
    else:
        ax.axhline(y=results['source_r2'], color='blue', linestyle='--', alpha=0.7, label='Source Domain')

    ax.legend()
    st.pyplot(fig)

    # Predictions analysis
    st.subheader("🔍 Prediction Analysis")

    # Create comparison dataframe
    comparison_df = pd.DataFrame({
        'True_Value': results['true_labels'],
        'Baseline_Prediction': results['baseline_predictions'],
        'Transfer_Prediction': results['target_predictions']
    })

    if problem_type == "classification":
        # Confusion matrices comparison
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Baseline Model**")
            from sklearn.metrics import confusion_matrix
            cm_baseline = confusion_matrix(results['true_labels'], results['baseline_predictions'])
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.heatmap(cm_baseline, annot=True, fmt='d', cmap='Blues', ax=ax)
            ax.set_title("Baseline Confusion Matrix")
            st.pyplot(fig)

        with col2:
            st.write("**Transfer Learning Model**")
            cm_transfer = confusion_matrix(results['true_labels'], results['target_predictions'])
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.heatmap(cm_transfer, annot=True, fmt='d', cmap='Blues', ax=ax)
            ax.set_title("Transfer Learning Confusion Matrix")
            st.pyplot(fig)
    else:
        # Regression plot
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(results['true_labels'], results['baseline_predictions'], alpha=0.6, label='Baseline', color='red')
        ax.scatter(results['true_labels'], results['target_predictions'], alpha=0.6, label='Transfer Learning', color='green')
        ax.plot([results['true_labels'].min(), results['true_labels'].max()],
               [results['true_labels'].min(), results['true_labels'].max()], 'k--', alpha=0.8)
        ax.set_xlabel('True Values')
        ax.set_ylabel('Predicted Values')
        ax.set_title('Regression: True vs Predicted')
        ax.legend()
        st.pyplot(fig)

    # Transfer learning insights
    st.subheader("🎯 Transfer Learning Insights")

    if results['transfer_gain'] > 0:
        st.success(f"✅ Transfer learning improved performance by {results['transfer_gain']:.3f}!")
        st.info("""
        **Positive Transfer**: Knowledge from the source domain successfully helped the target domain.
        This suggests the domains are related and the transfer method was effective.
        """)
    else:
        st.warning(f"⚠️ Transfer learning decreased performance by {abs(results['transfer_gain']):.3f}.")
        st.info("""
        **Negative Transfer**: The source domain knowledge may have hurt performance.
        Try adjusting the transfer strength or using a different transfer method.
        """)

    # Technical details
    st.subheader("🔧 Technical Details")

    details = f"""
    **Transfer Method**: {transfer_method}
    **Problem Type**: {problem_type}
    **Source Domain Size**: {len(results['source_predictions'])} samples
    **Target Domain Size**: {len(results['true_labels'])} samples

    **How it works**:
    1. Train a model on the source domain data
    2. Extract knowledge (feature importance, model parameters)
    3. Transfer this knowledge to help train on the target domain
    4. Fine-tune the model for optimal target performance
    """

    st.info(details)

    # Export results
    st.subheader("💾 Export Results")

    csv = comparison_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Transfer Learning Results",
        data=csv,
        file_name="transfer_learning_results.csv",
        mime="text/csv"
    )