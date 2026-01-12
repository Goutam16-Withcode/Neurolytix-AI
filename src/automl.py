import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, KFold, permutation_test_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import (
    accuracy_score, mean_squared_error, r2_score, classification_report, confusion_matrix, roc_curve, auc,
    precision_score, recall_score, f1_score, mean_absolute_error,
    balanced_accuracy_score, matthews_corrcoef, cohen_kappa_score, log_loss,
    mean_absolute_percentage_error, explained_variance_score, max_error
)
from sklearn.metrics import silhouette_score, davies_bouldin_score

import plotly.express as px
import plotly.graph_objects as go
from ui import section_header, apply_neuro_theme

from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.naive_bayes import GaussianNB 
from sklearn.ensemble import AdaBoostClassifier, AdaBoostRegressor
from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
from catboost import CatBoostClassifier, CatBoostRegressor
import optuna
import warnings
warnings.filterwarnings('ignore')

def get_model_recommendations(df, target_col):
    """Get intelligent model recommendations based on data characteristics"""
    try:
        problem_type = detect_problem_type(df, target_col)
        recommendations = []

        # Analyze data characteristics
        n_samples, n_features = df.shape
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns

        # NLP-specific recommendations
        if "NLP" in problem_type:
            recommendations = [
                ("TF-IDF + Logistic Regression", "Simple and effective for text classification", "High"),
                ("TF-IDF + Random Forest", "Handles text features well", "High"),
                ("TF-IDF + SVM", "Effective for high-dimensional text data", "Very High"),
                ("TF-IDF + XGBoost", "State-of-the-art performance", "Very High"),
                ("Naive Bayes (Multinomial)", "Specifically designed for text classification", "High")
            ]

            if n_samples > 10000:  # Large dataset
                recommendations.insert(0, ("TF-IDF + LightGBM", "Fast training on large text datasets", "Very High"))

        # Time Series recommendations
        elif "Time Series" in problem_type:
            recommendations = [
                ("ARIMA", "Classical time series forecasting", "High"),
                ("Prophet", "Handles seasonality and trends automatically", "Very High"),
                ("SARIMA", "Advanced seasonal ARIMA", "High"),
                ("Exponential Smoothing", "Good for trend and seasonality", "Medium"),
                ("LSTM Neural Network", "Deep learning for complex patterns", "High")
            ]

            # Check for seasonality
            if len(df) > 30:  # Enough data for seasonality detection
                try:
                    from dataset_intelligence import detect_dataset_type
                    detection = detect_dataset_type(df)
                    if 'seasonal' in str(detection.get('characteristics', {})):
                        recommendations.insert(0, ("Prophet", "Excellent for seasonal data", "Very High"))
                except:
                    pass

        # Classification recommendations
        elif problem_type == "Classification":
            y = df[target_col]
            n_classes = y.nunique()
            is_binary = n_classes == 2
            is_imbalanced = y.value_counts().min() / y.value_counts().max() < 0.1

            if is_binary:
                recommendations = [
                    ("Logistic Regression", "Simple, interpretable, good baseline", "High"),
                    ("Random Forest", "Handles mixed data, robust to overfitting", "High"),
                    ("XGBoost", "High performance, handles missing values", "Very High"),
                    ("LightGBM", "Fast training, good for large datasets", "High"),
                    ("CatBoost", "Excellent for categorical features", "High" if len(categorical_cols) > 0 else "Medium")
                ]
            else:
                recommendations = [
                    ("Random Forest", "Handles multi-class naturally", "High"),
                    ("XGBoost", "State-of-the-art performance", "Very High"),
                    ("LightGBM", "Fast and memory efficient", "High"),
                    ("CatBoost", "Great for categorical features", "High"),
                    ("SVM", "Effective for high-dimensional data", "Medium")
                ]

            if is_imbalanced:
                recommendations.insert(0, ("Balanced Random Forest", "Handles class imbalance well", "High"))

        # Regression recommendations
        elif problem_type == "Regression":
            # Check for outliers/high variance
            if numeric_cols.any():
                skewness = df[numeric_cols].skew().abs().mean()
                has_high_skew = skewness > 1

            recommendations = [
                ("Linear Regression", "Simple baseline, interpretable", "Medium"),
                ("Random Forest", "Handles non-linear relationships", "High"),
                ("XGBoost", "High performance regression", "Very High"),
                ("LightGBM", "Fast and accurate", "High"),
                ("Gradient Boosting", "Powerful ensemble method", "High")
            ]

            if has_high_skew:
                recommendations.insert(0, ("Robust Regression", "Handles outliers well", "Medium"))

        return recommendations, problem_type

    except Exception as e:
        return [("Random Forest", f"Default recommendation due to error: {str(e)}", "Medium")], "Unknown"

def quick_model_comparison(df, target_col, test_size=0.2):
    """Quick comparison of top recommended models"""
    try:
        recommendations, problem_type = get_model_recommendations(df, target_col)

        # Prepare data
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if target_col in numeric_cols:
            numeric_cols.remove(target_col)

        X = df[numeric_cols].fillna(df[numeric_cols].median())
        y = df[target_col]

        # Remove rows with missing target
        valid_idx = y.dropna().index
        X = X.loc[valid_idx]
        y = y.loc[valid_idx]

        if len(X) < 10:
            return None, "Insufficient data for comparison"

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

        results = []
        top_models = recommendations[:3]  # Test top 3 recommendations

        for model_name, description, confidence in top_models:
            try:
                if problem_type == "Classification":
                    if model_name == "Logistic Regression":
                        from sklearn.linear_model import LogisticRegression
                        model = LogisticRegression(max_iter=1000)
                    elif model_name == "Random Forest":
                        model = RandomForestClassifier(n_estimators=50, random_state=42)
                    elif model_name == "XGBoost":
                        model = XGBClassifier(n_estimators=50, random_state=42)
                    elif model_name == "LightGBM":
                        model = LGBMClassifier(n_estimators=50, random_state=42)
                    elif model_name == "CatBoost":
                        model = CatBoostClassifier(iterations=50, random_state=42, verbose=False)
                    else:
                        continue

                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)

                    if len(np.unique(y_test)) == 2:
                        accuracy = accuracy_score(y_test, y_pred)
                        f1 = f1_score(y_test, y_pred, average='weighted')
                        score = (accuracy + f1) / 2
                    else:
                        score = accuracy_score(y_test, y_pred)

                else:  # Regression
                    if model_name == "Linear Regression":
                        from sklearn.linear_model import LinearRegression
                        model = LinearRegression()
                    elif model_name == "Random Forest":
                        model = RandomForestRegressor(n_estimators=50, random_state=42)
                    elif model_name == "XGBoost":
                        model = XGBRegressor(n_estimators=50, random_state=42)
                    elif model_name == "LightGBM":
                        model = LGBMRegressor(n_estimators=50, random_state=42)
                    elif model_name == "Gradient Boosting":
                        model = GradientBoostingRegressor(n_estimators=50, random_state=42)
                    else:
                        continue

                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    score = r2_score(y_test, y_pred)

                results.append({
                    'model': model_name,
                    'score': score,
                    'description': description,
                    'confidence': confidence
                })

            except Exception as e:
                results.append({
                    'model': model_name,
                    'score': None,
                    'description': f"Failed: {str(e)}",
                    'confidence': confidence
                })

        return results, problem_type

    except Exception as e:
        return None, f"Comparison failed: {str(e)}"

def detect_problem_type(df, target_col):
    """
    Automatically detects if the problem is Regression, Classification, Time Series, or NLP.
    Enhanced with intelligent dataset type detection.
    """
    try:
        # First try the intelligent detection
        from dataset_intelligence import detect_dataset_type
        detection = detect_dataset_type(df)

        # If we have a target column, refine the detection
        if target_col and target_col in df.columns:
            y = df[target_col]

            # For NLP datasets, check if target is suitable for text classification
            if detection['dataset_type'] == 'NLP':
                if y.dtype == 'object' or y.nunique() < 20:
                    return "NLP (Text Classification)"
                else:
                    return "NLP (Text Regression)"

            # For Time Series, check if target is the value column
            elif detection['dataset_type'] == 'Time Series':
                if pd.api.types.is_numeric_dtype(y):
                    return "Time Series Forecasting"
                else:
                    return "Time Series Classification"

            # For tabular data, determine classification vs regression
            else:
                if pd.api.types.is_numeric_dtype(y):
                    if y.nunique() < 20:  # Heuristic threshold for classification
                        return "Classification"
                    else:
                        return "Regression"
                else:
                    return "Classification"
        else:
            # No target specified, return the general dataset type
            return detection['dataset_type']

    except ImportError:
        # Fallback to original logic if dataset_intelligence is not available
        y = df[target_col]

        # Check for Time Series (Date index or column)
        date_cols = df.select_dtypes(include=['datetime']).columns
        if len(date_cols) > 0:
            return "Time Series Forecasting"

        # Check for NLP
        if y.dtype == 'object' and df.select_dtypes(include=['object']).apply(lambda x: x.str.len().mean() > 50).any():
            return "NLP (Text Classification)"

        # Classification vs Regression
        if pd.api.types.is_numeric_dtype(y):
            if y.nunique() < 20: # Heuristic threshold
                return "Classification"
            else:
                return "Regression"
        else:
            return "Classification"

def show_automl(df):
    section_header("AutoML (Supervised)", "Train and evaluate models with ease.")
    
    # 1. Target Selection
    target = st.selectbox("Select Target Column", df.columns)
    
    if not target:
        return

    # Auto-Detect Problem Type
    detected_type = detect_problem_type(df, target)
    st.write(f"🔍 **Auto-Detected Problem Type**: `{detected_type}`")
    
    # Allow override
    problem_type = st.radio("Problem Type", ["Classification", "Regression", "NLP", "Time Series"], index=["Classification", "Regression", "NLP", "Time Series"].index(detected_type) if detected_type in ["Classification", "Regression", "NLP", "Time Series"] else 0)

    # AI Model Recommendation Engine
    with st.expander("🤖 AI Model Recommendations", expanded=True):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### Recommended Models")
            recommendations, _ = get_model_recommendations(df, target)

            for i, (model, desc, confidence) in enumerate(recommendations[:5]):
                confidence_color = {"Very High": "🟢", "High": "🟡", "Medium": "🟠", "Low": "🔴"}.get(confidence, "⚪")
                st.markdown(f"{i+1}. **{model}** {confidence_color}")
                st.caption(f"{desc} | Confidence: {confidence}")

        with col2:
            st.markdown("### Quick Comparison")
            if st.button("Compare Top 3 Models", key="quick_compare"):
                with st.spinner("Training and comparing models..."):
                    results, prob_type = quick_model_comparison(df, target)

                    if results:
                        st.markdown(f"**Problem Type:** {prob_type}")

                        # Sort by score
                        valid_results = [r for r in results if r['score'] is not None]
                        if valid_results:
                            best_model = max(valid_results, key=lambda x: x['score'])

                            for result in sorted(valid_results, key=lambda x: x['score'], reverse=True):
                                score_display = f"{result['score']:.3f}" if result['score'] is not None else "Failed"
                                is_best = "🏆" if result == best_model else ""
                                st.markdown(f"**{result['model']}** {is_best}: {score_display}")
                        else:
                            st.error("All model trainings failed")
                    else:
                        st.warning(prob_type)

    st.markdown("---")

    # 2. Problem Setup
    X = df.drop(columns=[target])
    y = df[target]

    # 3. Model Selection
    model_list = [
        "Random Forest", "Gradient Boosting", "Linear/Logistic Regression",
        "Support Vector Machine (SVM)", "K-Nearest Neighbors (KNN)",
        "Decision Tree", "AdaBoost", "XGBoost", "LightGBM", "CatBoost"
    ]
    if problem_type == "Classification":
        model_list.append("Naive Bayes")
        
    model_name = st.selectbox("Select Model", model_list)
    
    # 4. Parameters
    split_size = st.slider("Train/Test Split Ratio", 0.1, 0.9, 0.8)
    
    # 5. Hyperparameter Tuning
    enable_tuning = st.checkbox("🔮 Enable Hyperparameter Tuning (Optuna)")
    n_trials = 10
    if enable_tuning:
        n_trials = st.slider("Number of Trials", 5, 50, 10)
    
    if st.button("Train Model"):
        # Very basic preprocessing (handling NaNs and categorization) - simple version
        # In a real app, use the `cleaning` module first.
        # Dropping NaNs for MVP robustness
        X_clean = X.select_dtypes(include=[np.number]).dropna()
        # If dropping NaNs changed row count, align y
        y_clean = y[X_clean.index]
        
        # Train Split
        X_train, X_test, y_train, y_test = train_test_split(X_clean, y_clean, train_size=split_size, random_state=42)
        
        # Hyperparameter Optimization
        best_params = {}
        if enable_tuning:
            with st.spinner(f"Optimizing Hyperparameters ({n_trials} trials)..."):
                
                def objective(trial):
                    if model_name == "Random Forest":
                        n_estimators = trial.suggest_int('n_estimators', 50, 300)
                        max_depth = trial.suggest_int('max_depth', 2, 20)
                        if problem_type == "Classification":
                            m = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth)
                        else:
                            m = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth)
                    
                    elif model_name == "XGBoost":
                        lr = trial.suggest_float('learning_rate', 0.01, 0.3, log=True)
                        md = trial.suggest_int('max_depth', 3, 10)
                        if problem_type == "Classification":
                            m = XGBClassifier(use_label_encoder=False, eval_metric='logloss', learning_rate=lr, max_depth=md)
                        else:
                            m = XGBRegressor(learning_rate=lr, max_depth=md)
                            
                    elif model_name == "Support Vector Machine (SVM)":
                        c = trial.suggest_float('C', 0.1, 10.0, log=True)
                        if problem_type == "Classification":
                            m = SVC(C=c, probability=True)
                        else:
                            m = SVR(C=c)
                    
                    else:
                        # Fallback for models not explicitly tuned here for MVP
                        return 0 
                        
                    m.fit(X_train, y_train)
                    return m.score(X_test, y_test)

                if model_name in ["Random Forest", "XGBoost", "Support Vector Machine (SVM)"]:
                    study = optuna.create_study(direction="maximize")
                    study.optimize(objective, n_trials=n_trials)
                    best_params = study.best_params
                    st.success(f"Best Params Found: {best_params}")
                else:
                    st.warning(f"Tuning not yet implemented for {model_name}, using defaults.")

        # Instantiate Model with Best Params
        if problem_type == "Classification":
            if model_name == "Random Forest": model = RandomForestClassifier(**best_params)
            elif model_name == "Gradient Boosting": model = GradientBoostingClassifier()
            elif model_name == "Linear/Logistic Regression": model = LogisticRegression(max_iter=1000)
            elif model_name == "Support Vector Machine (SVM)": model = SVC(**best_params, probability=True)
            elif model_name == "K-Nearest Neighbors (KNN)": model = KNeighborsClassifier()
            elif model_name == "Decision Tree": model = DecisionTreeClassifier()
            elif model_name == "Naive Bayes": model = GaussianNB()
            elif model_name == "AdaBoost": model = AdaBoostClassifier()
            elif model_name == "XGBoost": model = XGBClassifier(use_label_encoder=False, eval_metric='logloss', **best_params)
            elif model_name == "LightGBM": model = LGBMClassifier()
            elif model_name == "CatBoost": model = CatBoostClassifier(verbose=0)
            
        else: # Regression
            if model_name == "Random Forest": model = RandomForestRegressor(**best_params)
            elif model_name == "Gradient Boosting": model = GradientBoostingRegressor()
            elif model_name == "Linear/Logistic Regression": model = LinearRegression()
            elif model_name == "Support Vector Machine (SVM)": model = SVR(**best_params)
            elif model_name == "K-Nearest Neighbors (KNN)": model = KNeighborsRegressor()
            elif model_name == "Decision Tree": model = DecisionTreeRegressor()
            elif model_name == "AdaBoost": model = AdaBoostRegressor()
            elif model_name == "XGBoost": model = XGBRegressor(**best_params)
            elif model_name == "LightGBM": model = LGBMRegressor()
            elif model_name == "CatBoost": model = CatBoostRegressor(verbose=0)
        
        # Train
        with st.spinner("Training Final Model..."):
            model.fit(X_train, y_train)
            
        st.success("Training Complete!")
        
        if st.checkbox("Save Model to Session (for Deployment)"):
            st.session_state['model'] = model
            st.success("Model saved! Go to 'Model Deployment' to download it.")
        
        # Predictions
        y_pred = model.predict(X_test)
        
        # Evaluation
        st.subheader("Model Evaluation")
        
        if problem_type == "Classification":
            # Basic Metrics
            acc = accuracy_score(y_test, y_pred)

            # Handle multi-class vs binary robustly (support non-numeric labels)
            y_true_series = pd.Series(y_test)
            unique_labels = y_true_series.unique().tolist()
            is_multiclass = len(unique_labels) > 2

            try:
                if is_multiclass:
                    prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
                    rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
                    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
                else:
                    # Binary case: determine pos_label if labels are non-numeric
                    if len(unique_labels) == 2:
                        pos_label = unique_labels[1]
                        prec = precision_score(y_test, y_pred, pos_label=pos_label, zero_division=0)
                        rec = recall_score(y_test, y_pred, pos_label=pos_label, zero_division=0)
                        f1 = f1_score(y_test, y_pred, pos_label=pos_label, zero_division=0)
                    else:
                        # Edge case: single-class in test set - fallback
                        prec = precision_score(y_test, y_pred, average='binary', zero_division=0)
                        rec = recall_score(y_test, y_pred, average='binary', zero_division=0)
                        f1 = f1_score(y_test, y_pred, average='binary', zero_division=0)
            except ValueError:
                # As a safe fallback, use weighted averages
                prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
                rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
                f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)

            bal_acc = balanced_accuracy_score(y_test, y_pred)
            mcc = matthews_corrcoef(y_test, y_pred)
            kappa = cohen_kappa_score(y_test, y_pred)
            
            st.write("### 📊 Classification Metrics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown('<div class="neuro-card">', unsafe_allow_html=True)
                st.metric("Accuracy", f"{acc:.2%}")
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="neuro-card">', unsafe_allow_html=True)
                st.metric("Precision", f"{prec:.2%}")
                st.markdown('</div>', unsafe_allow_html=True)
            with col3:
                st.markdown('<div class="neuro-card">', unsafe_allow_html=True)
                st.metric("Recall", f"{rec:.2%}")
                st.markdown('</div>', unsafe_allow_html=True)
            with col4:
                st.markdown('<div class="neuro-card">', unsafe_allow_html=True)
                st.metric("F1 Score", f"{f1:.2%}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            col5, col6, col7, col8 = st.columns(4)
            col5.metric("Balanced Acc", f"{bal_acc:.2%}")
            col6.metric("MCC", f"{mcc:.4f}")
            col7.metric("Kappa", f"{kappa:.4f}")
            
            if hasattr(model, "predict_proba"):
                try:
                    y_prob = model.predict_proba(X_test)
                    ll = log_loss(y_test, y_prob)
                    col8.metric("Log Loss", f"{ll:.4f}")
                except:
                    col8.metric("Log Loss", "N/A")

            # --- Baseline & Significance Checks (detect random-like performance)
            try:
                st.markdown('### 🔬 Baseline & Significance Checks')
                # Majority-class baseline
                majority_acc = pd.Series(y_test).value_counts(normalize=True).max()
                unique_labels = pd.Series(y_test).unique().tolist()
                n_classes = len(unique_labels)
                random_acc = 1.0 / n_classes if n_classes > 0 else 0.0

                # Cross-validated accuracy
                try:
                    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
                    cv_scores = cross_val_score(model, X_clean, y_clean, cv=cv, scoring='accuracy')
                    cv_mean = float(cv_scores.mean())
                except Exception:
                    cv_mean = None

                # Permutation test (small number of permutations for speed)
                perm_pvalue = None
                perm_score = None
                try:
                    n_perms = 100 if len(X_test) > 50 else 500
                    score, perm_scores, pvalue = permutation_test_score(model, X_test, y_test, scoring='accuracy', n_permutations=min(n_perms, 500), random_state=42)
                    perm_score = float(score)
                    perm_pvalue = float(pvalue)
                except Exception:
                    perm_pvalue = None
                    perm_score = None

                # Show results
                cA, cB, cC = st.columns(3)
                with cA:
                    st.metric('Model Acc', f"{acc:.2%}")
                    if cv_mean is not None:
                        st.caption(f"CV Acc (5-fold): {cv_mean:.2%}")
                with cB:
                    st.metric('Majority Baseline', f"{majority_acc:.2%}")
                    st.caption(f"Random Guess (uniform): {random_acc:.2%}")
                with cC:
                    if perm_pvalue is not None:
                        st.metric('Perm p-value', f"{perm_pvalue:.4f}")
                        st.caption(f"Perm score: {perm_score:.2%}")
                    else:
                        st.caption('Permutation test unavailable')

                # Issue warnings when performance is suspiciously low
                safe_margin = 0.02
                if acc <= max(majority_acc, random_acc) + safe_margin:
                    st.warning('Model performance is close to or worse than trivial baselines (majority/random).')
                elif perm_pvalue is not None and perm_pvalue > 0.05:
                    st.warning('Permutation p-value > 0.05: model may not be significantly better than chance.')
            except Exception:
                # Do not fail evaluation if baseline checks error
                pass

            # Actual vs Predicted Scatter Plot for Classification
            st.subheader("Actual vs Predicted Analysis")
            # Create a dataframe for visualization
            pred_df = pd.DataFrame({
                'Actual': y_test,
                'Predicted': y_pred,
                'Correct': (y_test == y_pred).astype(int)
            })

            # Color by correctness
            color_map = {0: 'red', 1: 'green'}
            color_labels = {0: 'Incorrect', 1: 'Correct'}

            fig_actual_pred_class = px.scatter(
                pred_df,
                x='Actual',
                y='Predicted',
                color='Correct',
                color_discrete_map=color_map,
                labels={'Correct': 'Prediction'},
                title="Actual vs Predicted (Classification)",
                category_orders={'Correct': [0, 1]}
            )

            # Update color labels
            fig_actual_pred_class.for_each_trace(lambda t: t.update(name=color_labels[int(t.name)]))

            fig_actual_pred_class.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Actual Values",
                yaxis_title="Predicted Values"
            )
            st.plotly_chart(apply_neuro_theme(fig_actual_pred_class), use_container_width=True, theme=None)

            # Confusion Matrix
            cm = confusion_matrix(y_test, y_pred)
            fig_cm = px.imshow(cm, text_auto=True, title="Confusion Matrix", color_continuous_scale='Blues')
            fig_cm.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(apply_neuro_theme(fig_cm), use_container_width=True, theme=None)
            
            # ROC Curve (Binary only for MVP simplification, can expand to Multi-class)
            if not is_multiclass:
                if hasattr(model, "predict_proba"):
                    try:
                        proba = model.predict_proba(X_test)

                        # Determine positive label and corresponding probability column
                        if hasattr(model, "classes_"):
                            classes = list(model.classes_)
                            # Prefer human-sensible positive labels if present
                            preferred = None
                            for candidate in ["Presence", "presence", "Yes", "yes", 1, "1", True]:
                                if candidate in classes:
                                    preferred = candidate
                                    break
                            pos_label = preferred if preferred is not None else (classes[1] if len(classes) > 1 else classes[0])
                            idx = classes.index(pos_label)
                            y_prob_pos = proba[:, idx]
                            # Create binary true labels for ROC
                            y_true_bin = (pd.Series(y_test) == pos_label).astype(int)
                        else:
                            # Fallback: assume second column corresponds to positive class
                            y_prob_pos = proba[:, 1] if proba.ndim == 2 else proba
                            y_true_bin = pd.Series(y_test).astype(int)

                        fpr, tpr, _ = roc_curve(y_true_bin, y_prob_pos)
                        roc_auc = auc(fpr, tpr)

                        fig_roc = go.Figure()
                        fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, name=f"AUC = {roc_auc:.2f}"))
                        fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', line=dict(dash='dash'), name='Random'))
                        fig_roc.update_layout(title="ROC Curve", xaxis_title="False Positive Rate", yaxis_title="True Positive Rate", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(apply_neuro_theme(fig_roc), use_container_width=True, theme=None)
                    except Exception as e:
                        st.warning(f"ROC curve not available for this model: {e}")
            
        else:
            # Regression Metrics
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            mape = mean_absolute_percentage_error(y_test, y_pred)
            evs = explained_variance_score(y_test, y_pred)
            me = max_error(y_test, y_pred)
            
            st.write("### 📉 Regression Metrics")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown('<div class="neuro-card">', unsafe_allow_html=True)
                st.metric("R2 Score", f"{r2:.4f}")
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="neuro-card">', unsafe_allow_html=True)
                st.metric("RMSE", f"{rmse:.4f}")
                st.markdown('</div>', unsafe_allow_html=True)
            with c3:
                st.markdown('<div class="neuro-card">', unsafe_allow_html=True)
                st.metric("MSE", f"{mse:.4f}")
                st.markdown('</div>', unsafe_allow_html=True)
            with c4:
                st.markdown('<div class="neuro-card">', unsafe_allow_html=True)
                st.metric("MAE", f"{mae:.4f}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            c5, c6, c7, c8 = st.columns(4)
            c5.metric("MAPE", f"{mape:.2%}")
            c6.metric("Expl. Variance", f"{evs:.4f}")
            c7.metric("Max Error", f"{me:.4f}")

            # --- Baseline & Significance Checks for Regression
            try:
                st.markdown('### 🔬 Baseline & Significance Checks')

                # Simple baseline: predict mean of training target
                mean_baseline = np.mean(y_train)
                mean_predictions = np.full_like(y_test, mean_baseline)
                mean_mse = mean_squared_error(y_test, mean_predictions)
                mean_rmse = np.sqrt(mean_mse)
                mean_mae = mean_absolute_error(y_test, mean_predictions)

                # Model performance
                model_mse = mean_squared_error(y_test, y_pred)
                model_rmse = np.sqrt(model_mse)
                model_mae = mean_absolute_error(y_test, y_pred)

                # Cross-validated performance
                try:
                    from sklearn.model_selection import cross_val_score, KFold
                    cv = KFold(n_splits=5, shuffle=True, random_state=42)
                    cv_scores = cross_val_score(model, X_clean, y_clean, cv=cv, scoring='neg_mean_squared_error')
                    cv_mse_mean = -float(cv_scores.mean())
                    cv_rmse_mean = np.sqrt(cv_mse_mean)
                except Exception:
                    cv_mse_mean = None
                    cv_rmse_mean = None

                # Display results
                cA, cB, cC = st.columns(3)
                with cA:
                    st.metric('Model RMSE', f"{model_rmse:.4f}")
                    if cv_rmse_mean is not None:
                        st.caption(f"CV RMSE: {cv_rmse_mean:.4f}")
                with cB:
                    st.metric('Mean Baseline RMSE', f"{mean_rmse:.4f}")
                    st.caption("Predicting training mean")
                with cC:
                    improvement = ((mean_rmse - model_rmse) / mean_rmse) * 100
                    st.metric('Improvement over Mean', f"{improvement:.1f}%")
                    if improvement > 0:
                        st.caption("✅ Better than mean baseline")
                    else:
                        st.caption("⚠️ Worse than mean baseline")

                # Significance test (simple t-test on residuals vs mean baseline)
                try:
                    from scipy import stats
                    model_residuals = y_test - y_pred
                    mean_residuals = y_test - mean_predictions

                    # Test if model residuals are significantly different from mean baseline residuals
                    t_stat, p_value = stats.ttest_ind(model_residuals, mean_residuals, equal_var=False)

                    st.info(f"**Significance Test**: Model vs Mean Baseline (p-value: {p_value:.4f})")
                    if p_value < 0.05:
                        st.success("✅ Model performance is statistically significant vs mean baseline")
                    else:
                        st.warning("⚠️ Model performance is not significantly different from mean baseline")

                except Exception:
                    st.caption("Significance test unavailable")

            except Exception as e:
                st.warning(f"Baseline checks failed: {str(e)}")

            # Actual vs Predicted Analysis
            st.subheader("Actual vs Predicted Analysis")

            # Create enhanced scatter plot with color coding
            pred_df_reg = pd.DataFrame({
                'Actual': y_test,
                'Predicted': y_pred,
                'Residual': y_test - y_pred,
                'Absolute_Error': abs(y_test - y_pred)
            })

            # Color by residual magnitude (closer to perfect = green, larger errors = red)
            pred_df_reg['Error_Category'] = pd.cut(
                pred_df_reg['Absolute_Error'],
                bins=[-np.inf, pred_df_reg['Absolute_Error'].quantile(0.33),
                      pred_df_reg['Absolute_Error'].quantile(0.67), np.inf],
                labels=['Low Error', 'Medium Error', 'High Error']
            )

            color_map_reg = {'Low Error': 'green', 'Medium Error': 'orange', 'High Error': 'red'}

            fig_actual_pred_reg = px.scatter(
                pred_df_reg,
                x='Actual',
                y='Predicted',
                color='Error_Category',
                color_discrete_map=color_map_reg,
                labels={'Error_Category': 'Prediction Accuracy'},
                title="Actual vs Predicted (Regression) - Colored by Error Magnitude",
                opacity=0.7,
                hover_data=['Residual', 'Absolute_Error']
            )

            # Add perfect prediction line
            fig_actual_pred_reg.add_shape(
                type="line",
                line=dict(dash='dash', color='white', width=2),
                x0=y_test.min(),
                y0=y_test.min(),
                x1=y_test.max(),
                y1=y_test.max()
            )

            fig_actual_pred_reg.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Actual Values",
                yaxis_title="Predicted Values"
            )
            st.plotly_chart(apply_neuro_theme(fig_actual_pred_reg), use_container_width=True, theme=None)

            # Additional plots in columns
            c_p1, c_p2 = st.columns(2)

            # 1. Residual Plot
            residuals = y_test - y_pred
            fig_res = px.scatter(x=y_pred, y=residuals, labels={'x': 'Predicted', 'y': 'Residuals'}, title="Residual Plot")
            fig_res.add_hline(y=0, line_dash="dash", line_color="red")
            fig_res.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            c_p1.plotly_chart(apply_neuro_theme(fig_res), use_container_width=True, theme=None)

            # 2. Prediction Tracking Curve (Line Plot for first 100 samples)
            comparison_df = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred}).reset_index(drop=True).head(100)
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(y=comparison_df['Actual'], mode='lines+markers', name='Actual', line=dict(color='#00d2ff')))
            fig_line.add_trace(go.Scatter(y=comparison_df['Predicted'], mode='lines+markers', name='Predicted', line=dict(color='#ff00cc', dash='dot')))
            fig_line.update_layout(title="Prediction Tracking Curve (First 100 Samples)", xaxis_title="Sample Index", yaxis_title="Target Value", hovermode="x unified",
                                 template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            c_p2.plotly_chart(apply_neuro_theme(fig_line), use_container_width=True, theme=None)

            
        # Feature Importance
        if hasattr(model, "feature_importances_"):
            st.subheader("Feature Importance")
            fi = pd.DataFrame({
                'Feature': X_clean.columns,
                'Importance': model.feature_importances_
            }).sort_values(by='Importance', ascending=False)
            
            fig_fi = px.bar(fi, x='Importance', y='Feature', orientation='h', title="Feature Importance")
            st.plotly_chart(apply_neuro_theme(fig_fi), use_container_width=True, theme=None)
            
        # -------------------------
        # EXPLAINABLE AI (XAI) - SHAP
        # -------------------------
        st.subheader("Explainable AI (SHAP)")
        import shap
        import matplotlib.pyplot as plt
        
        if st.checkbox("Run SHAP Analysis (May be slow)"):
            with st.spinner("Calculating SHAP values..."):
                # Use TreeExplainer for tree-based models
                # For basic MVP we assume Tree based as per our selection list
                # (Linear Regression would need LinearExplainer)
                try:
                    explainer = shap.Explainer(model, X_train)
                    shap_values = explainer(X_test)
                    
                    st.write("### SHAP Summary Plot")
                    st.write("Features sorting by their impact on model output.")
                    fig, ax = plt.subplots()
                    shap.summary_plot(shap_values, X_test, show=False)
                    st.pyplot(fig)
                    
                except Exception as e:
                    st.warning(f"SHAP failed: {e}. (Some models like Linear Regression might need different Explainer)")
