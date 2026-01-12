import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, r2_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_curve, auc, log_loss
)
from sklearn.model_selection import cross_val_score, StratifiedKFold, permutation_test_score
import optuna
import plotly.express as px
import plotly.graph_objects as go
from ui import section_header, apply_neuro_theme

def run_autonomous_mode(df):
    section_header("Autonomous Data Scientist", "Sit back while the AI handles the entire lifecycle.")
    
    st.info("This mode will automatically: 1. Clean Data, 2. Encode Features, 3. Select Target, 4. Train Model, 5. Report Results.")
    
    # 1. Target Selection (The only manual step needed usually)
    target = st.selectbox("Select Target Variable (What to predict?)", df.columns)

    # Detect problem type **early** so UI shows appropriate model choices
    y_sample = df[target]
    is_classification = False
    if y_sample.dtype == 'object' or y_sample.nunique() < 20:
        is_classification = True

    # Model option lists tailored to problem type
    classification_options = ["Random Forest", "Gradient Boosting", "Logistic Regression", "SVM", "KNN", "Decision Tree", "AdaBoost", "XGBoost", "LightGBM", "CatBoost", "Naive Bayes"]
    regression_options = ["Random Forest", "Gradient Boosting", "Linear Regression", "SVR", "KNN", "Decision Tree", "AdaBoost", "XGBoost", "LightGBM", "CatBoost"]

    # Keep UI minimal by default — advanced options hidden behind a toggle
    advanced = st.checkbox("Show advanced options (model list, tuning, diagnostics)", value=False)
    if advanced:
        models_to_consider = st.multiselect(
            "Models to consider (if trying multiple)",
            options=classification_options if is_classification else regression_options,
            default=["Random Forest", "Gradient Boosting", "XGBoost", "LightGBM"]
        )
        enable_tuning_opt = st.checkbox("Enable hyperparameter tuning for best model (slower)", value=False)
        tune_trials = st.slider("Tuning trials", 5, 50, 10) if enable_tuning_opt else 0
    else:
        # Defaults when advanced UI is hidden — choose common models for the detected problem type
        models_to_consider = ["Random Forest", "Gradient Boosting", "XGBoost", "LightGBM"] if is_classification else ["Random Forest", "Gradient Boosting", "XGBoost", "LightGBM"]
        enable_tuning_opt = False
        tune_trials = 0

    if st.button("🚀 Launch Autonomous Mission"):
        # Quiet mode (spinner) when advanced UI is hidden
        progress_bar = st.progress(0) if advanced else None
        status_text = st.empty() if advanced else None

        def _update_progress(pct=None, text=None):
            if progress_bar is not None and pct is not None:
                progress_bar.progress(pct)
            if status_text is not None and text is not None:
                status_text.text(text)

        try:
            # Use a single spinner for quiet mode, otherwise update detailed progress
            if advanced:
                _update_progress(None, "Step 1/6: Cleaning Data...")
                df_clean = df.copy()
                # Drop high null columns
                df_clean = df_clean.dropna(thresh=len(df)*0.5, axis=1)

                # Impute
                num_cols = df_clean.select_dtypes(include=['float64', 'int64']).columns
                cat_cols = df_clean.select_dtypes(include=['object']).columns

                if len(num_cols) > 0:
                    imputer_num = SimpleImputer(strategy='median')
                    df_clean[num_cols] = imputer_num.fit_transform(df_clean[num_cols])

                if len(cat_cols) > 0:
                    imputer_cat = SimpleImputer(strategy='most_frequent')
                    df_clean[cat_cols] = imputer_cat.fit_transform(df_clean[cat_cols])

                _update_progress(20, "Step 2/6: Encoding Variables...")
                le_dict = {}
                for col in cat_cols:
                    le = LabelEncoder()
                    df_clean[col] = le.fit_transform(df_clean[col].astype(str))
                    le_dict[col] = le
                _update_progress(40, "Step 3/6: Preparing Training Sets...")
                X = df_clean.drop(columns=[target])
                y = df_clean[target]

                # Detect Problem Type
                is_classification = False
                if y.dtype == 'object' or y.nunique() < 20:
                    is_classification = True
                    if y.dtype == 'object':
                        le_target = LabelEncoder()
                        y = le_target.fit_transform(y)

                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                _update_progress(60, None)
            else:
                with st.spinner('Working...'):
                    df_clean = df.copy()
                    df_clean = df_clean.dropna(thresh=len(df)*0.5, axis=1)
                    num_cols = df_clean.select_dtypes(include=['float64', 'int64']).columns
                    cat_cols = df_clean.select_dtypes(include=['object']).columns
                    if len(num_cols) > 0:
                        imputer_num = SimpleImputer(strategy='median')
                        df_clean[num_cols] = imputer_num.fit_transform(df_clean[num_cols])
                    if len(cat_cols) > 0:
                        imputer_cat = SimpleImputer(strategy='most_frequent')
                        df_clean[cat_cols] = imputer_cat.fit_transform(df_clean[cat_cols])

                    # Encoding
                    le_dict = {}
                    for col in cat_cols:
                        le = LabelEncoder()
                        df_clean[col] = le.fit_transform(df_clean[col].astype(str))
                        le_dict[col] = le

                    # Prepare sets
                    X = df_clean.drop(columns=[target])
                    y = df_clean[target]
                    if y.dtype == 'object' or y.nunique() < 20:
                        if y.dtype == 'object':
                            le_target = LabelEncoder()
                            y = le_target.fit_transform(y)
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Step 4: Model Search & Training
            # If in quiet mode (advanced == False), start a single 'Working...' spinner which we'll close later
            if not advanced:
                _spinner = st.spinner('Working...')
                _spinner.__enter__()

            _update_progress(None, f"Step 4/6: Searching & Training {'Classifier' if is_classification else 'Regressor'}...")
            
            # Determine candidates
            results = []
            best_model = None
            best_name = None
            best_score = -999

            if is_classification and models_to_consider:
                for name in models_to_consider:
                    try:
                        if name == 'Random Forest':
                            m = RandomForestClassifier(n_estimators=100, random_state=42)
                        elif name == 'Gradient Boosting':
                            from sklearn.ensemble import GradientBoostingClassifier
                            m = GradientBoostingClassifier()
                        elif name == 'Logistic Regression':
                            from sklearn.linear_model import LogisticRegression
                            m = LogisticRegression(max_iter=1000)
                        elif name == 'SVM':
                            from sklearn.svm import SVC
                            m = SVC(probability=True)  # enable predict_proba where possible
                        elif name == 'KNN':
                            from sklearn.neighbors import KNeighborsClassifier
                            m = KNeighborsClassifier()
                        elif name == 'Decision Tree':
                            from sklearn.tree import DecisionTreeClassifier
                            m = DecisionTreeClassifier()
                        elif name == 'AdaBoost':
                            from sklearn.ensemble import AdaBoostClassifier
                            m = AdaBoostClassifier()
                        elif name == 'XGBoost':
                            try:
                                from xgboost import XGBClassifier
                                m = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
                            except Exception:
                                m = RandomForestClassifier()
                        elif name == 'LightGBM':
                            try:
                                from lightgbm import LGBMClassifier
                                m = LGBMClassifier()
                            except Exception:
                                m = RandomForestClassifier()
                        elif name == 'CatBoost':
                            try:
                                from catboost import CatBoostClassifier
                                m = CatBoostClassifier(verbose=0)
                            except Exception:
                                m = RandomForestClassifier()
                        elif name == 'Naive Bayes':
                            from sklearn.naive_bayes import GaussianNB
                            m = GaussianNB()
                        else:
                            m = RandomForestClassifier()

                        m.fit(X_train, y_train)
                        y_pred_tmp = m.predict(X_test)
                        score_tmp = accuracy_score(y_test, y_pred_tmp)
                        results.append({'Model': name, 'Score': score_tmp, 'ModelObj': m})

                        if score_tmp > best_score:
                            best_score = score_tmp
                            best_model = m
                            best_name = name

                    except Exception:
                        # ignore failing candidate and continue
                        continue
            elif (not is_classification) and models_to_consider:
                from sklearn.ensemble import GradientBoostingRegressor
                from sklearn.linear_model import LinearRegression
                from sklearn.svm import SVR
                from sklearn.neighbors import KNeighborsRegressor
                from sklearn.tree import DecisionTreeRegressor
                from sklearn.ensemble import AdaBoostRegressor
                for name in models_to_consider:
                    try:
                        if name == 'Random Forest':
                            m = RandomForestRegressor(n_estimators=100, random_state=42)
                        elif name == 'Gradient Boosting':
                            m = GradientBoostingRegressor()
                        elif name == 'Linear Regression':
                            m = LinearRegression()
                        elif name == 'SVR':
                            m = SVR()
                        elif name == 'KNN':
                            m = KNeighborsRegressor()
                        elif name == 'Decision Tree':
                            m = DecisionTreeRegressor()
                        elif name == 'AdaBoost':
                            m = AdaBoostRegressor()
                        elif name == 'XGBoost':
                            try:
                                from xgboost import XGBRegressor
                                m = XGBRegressor()
                            except Exception:
                                m = RandomForestRegressor()
                        elif name == 'LightGBM':
                            try:
                                from lightgbm import LGBMRegressor
                                m = LGBMRegressor()
                            except Exception:
                                m = RandomForestRegressor()
                        elif name == 'CatBoost':
                            try:
                                from catboost import CatBoostRegressor
                                m = CatBoostRegressor(verbose=0)
                            except Exception:
                                m = RandomForestRegressor()
                        else:
                            m = RandomForestRegressor()

                        m.fit(X_train, y_train)
                        y_pred_tmp = m.predict(X_test)
                        score_tmp = r2_score(y_test, y_pred_tmp)
                        results.append({'Model': name, 'Score': score_tmp, 'ModelObj': m})

                        if score_tmp > best_score:
                            best_score = score_tmp
                            best_model = m
                            best_name = name

                    except Exception:
                        continue

            else:
                # Default to RandomForest if not exploring
                best_model = RandomForestClassifier(n_estimators=100, random_state=42) if is_classification else RandomForestRegressor(n_estimators=100, random_state=42)
                best_model.fit(X_train, y_train)
                best_name = 'Random Forest'
                best_score = accuracy_score(y_test, best_model.predict(X_test)) if is_classification else r2_score(y_test, best_model.predict(X_test))

            _update_progress(80, None)

            # Optionally tune only the best model (targeted tuning saves time)
            if enable_tuning_opt and best_name in ['Random Forest', 'XGBoost', 'LightGBM', 'Gradient Boosting']:
                _update_progress(None, 'Tuning best model...')
                try:
                    def objective(trial):
                        # Classification tuning
                        if is_classification:
                            if best_name == 'Random Forest':
                                n_estimators = trial.suggest_int('n_estimators', 50, 300)
                                max_depth = trial.suggest_int('max_depth', 2, 20)
                                m2 = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
                            elif best_name == 'XGBoost':
                                lr = trial.suggest_float('learning_rate', 0.01, 0.3, log=True)
                                md = trial.suggest_int('max_depth', 3, 10)
                                from xgboost import XGBClassifier
                                m2 = XGBClassifier(use_label_encoder=False, eval_metric='logloss', learning_rate=lr, max_depth=md)
                            elif best_name == 'LightGBM':
                                lr = trial.suggest_float('learning_rate', 0.01, 0.3, log=True)
                                md = trial.suggest_int('max_depth', 3, 16)
                                from lightgbm import LGBMClassifier
                                m2 = LGBMClassifier(learning_rate=lr, max_depth=md)
                            elif best_name == 'Gradient Boosting':
                                n_estimators = trial.suggest_int('n_estimators', 50, 300)
                                max_depth = trial.suggest_int('max_depth', 2, 20)
                                from sklearn.ensemble import GradientBoostingClassifier
                                m2 = GradientBoostingClassifier(n_estimators=n_estimators, max_depth=max_depth)
                            else:
                                return 0

                            m2.fit(X_train, y_train)
                            preds = m2.predict(X_test)
                            return accuracy_score(y_test, preds)

                        # Regression tuning
                        else:
                            if best_name == 'Random Forest':
                                n_estimators = trial.suggest_int('n_estimators', 50, 300)
                                max_depth = trial.suggest_int('max_depth', 2, 20)
                                m2 = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
                            elif best_name == 'XGBoost':
                                lr = trial.suggest_float('learning_rate', 0.01, 0.3, log=True)
                                md = trial.suggest_int('max_depth', 3, 10)
                                from xgboost import XGBRegressor
                                m2 = XGBRegressor(learning_rate=lr, max_depth=md)
                            elif best_name == 'LightGBM':
                                lr = trial.suggest_float('learning_rate', 0.01, 0.3, log=True)
                                md = trial.suggest_int('max_depth', 3, 16)
                                from lightgbm import LGBMRegressor
                                m2 = LGBMRegressor(learning_rate=lr, max_depth=md)
                            elif best_name == 'Gradient Boosting':
                                n_estimators = trial.suggest_int('n_estimators', 50, 300)
                                max_depth = trial.suggest_int('max_depth', 2, 20)
                                from sklearn.ensemble import GradientBoostingRegressor
                                m2 = GradientBoostingRegressor(n_estimators=n_estimators, max_depth=max_depth)
                            else:
                                return 0

                            m2.fit(X_train, y_train)
                            preds = m2.predict(X_test)
                            return r2_score(y_test, preds)

                    study = optuna.create_study(direction='maximize')
                    study.optimize(objective, n_trials=tune_trials)
                    best_params = study.best_params
                    _update_progress(None, 'Re-training with best parameters...')

                    if is_classification:
                        if best_name == 'Random Forest':
                            best_model = RandomForestClassifier(**best_params)
                        elif best_name == 'XGBoost':
                            from xgboost import XGBClassifier
                            best_model = XGBClassifier(use_label_encoder=False, eval_metric='logloss', **best_params)
                        elif best_name == 'LightGBM':
                            from lightgbm import LGBMClassifier
                            best_model = LGBMClassifier(**best_params)
                        elif best_name == 'Gradient Boosting':
                            from sklearn.ensemble import GradientBoostingClassifier
                            best_model = GradientBoostingClassifier(**best_params)
                    else:
                        if best_name == 'Random Forest':
                            best_model = RandomForestRegressor(**best_params)
                        elif best_name == 'XGBoost':
                            from xgboost import XGBRegressor
                            best_model = XGBRegressor(**best_params)
                        elif best_name == 'LightGBM':
                            from lightgbm import LGBMRegressor
                            best_model = LGBMRegressor(**best_params)
                        elif best_name == 'Gradient Boosting':
                            from sklearn.ensemble import GradientBoostingRegressor
                            best_model = GradientBoostingRegressor(**best_params)

                    best_model.fit(X_train, y_train)
                    best_score = accuracy_score(y_test, best_model.predict(X_test)) if is_classification else r2_score(y_test, best_model.predict(X_test))
                except Exception as e:
                    st.warning(f'Hyperparameter tuning failed: {e}')

            _update_progress(90, None)

            # Step 5: Evaluation
            _update_progress(None, 'Step 5/6: Evaluating Performance...')
            model = best_model
            y_pred = model.predict(X_test)

            _update_progress(100, 'Mission Complete! 🏁')
            
            # Report
            st.success("Model Trained Successfully!")

            # Close spinner if quiet mode
            if not advanced:
                try:
                    _spinner.__exit__(None, None, None)
                except Exception:
                    pass

            # Classification-specific reporting
            if is_classification:
                # Basic metrics
                acc = accuracy_score(y_test, y_pred)
                is_multiclass = len(pd.Series(y_test).unique()) > 2
                avg_method = 'weighted' if is_multiclass else 'binary'
                prec = precision_score(y_test, y_pred, average=avg_method, zero_division=0)
                rec = recall_score(y_test, y_pred, average=avg_method, zero_division=0)
                f1 = f1_score(y_test, y_pred, average=avg_method, zero_division=0)

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Accuracy", f"{acc:.2%}")
                with col2:
                    st.metric("Precision", f"{prec:.2%}")
                with col3:
                    st.metric("Recall", f"{rec:.2%}")
                with col4:
                    st.metric("F1 Score", f"{f1:.2%}")

                # Compact summary card and downloads
                try:
                    summary = {
                        'model': best_name if 'best_name' in locals() else type(model).__name__,
                        'accuracy': float(acc),
                        'precision': float(prec),
                        'recall': float(rec),
                        'f1': float(f1)
                    }
                    summary_df = pd.DataFrame([summary])
                    csv = summary_df.to_csv(index=False)
                    js = summary_df.to_json(orient='records')

                    s1, s2 = st.columns([3,1])
                    with s1:
                        st.markdown('#### Run Summary')
                        st.write(f"**Model:** {summary['model']}")
                        st.write(f"**Accuracy:** {summary['accuracy']:.2%}  •  **Precision:** {summary['precision']:.2%}  •  **Recall:** {summary['recall']:.2%}")
                    with s2:
                        st.download_button('Download CSV', csv, file_name='autonomous_summary.csv', mime='text/csv')
                        st.download_button('Download JSON', js, file_name='autonomous_summary.json', mime='application/json')
                        if st.button('Show JSON'):
                            st.code(js)
                except Exception:
                    pass

                # Show main visuals only: confusion matrix and (binary) ROC curve. Keep detailed reports collapsed into an "Advanced Results" expander.
                try:
                    cm = confusion_matrix(y_test, y_pred)
                    fig_cm = px.imshow(cm, text_auto=True, title="Confusion Matrix", color_continuous_scale='Blues')
                    fig_cm.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(apply_neuro_theme(fig_cm), use_container_width=True)
                except Exception:
                    st.warning("Could not compute confusion matrix.")

                if hasattr(model, "predict_proba") and not is_multiclass:
                    try:
                        proba = model.predict_proba(X_test)
                        if hasattr(model, "classes_"):
                            classes = list(model.classes_)
                            preferred = None
                            for candidate in ["Presence", "presence", "Yes", "yes", 1, "1", True]:
                                if candidate in classes:
                                    preferred = candidate
                                    break
                            pos_label = preferred if preferred is not None else (classes[1] if len(classes) > 1 else classes[0])
                            idx = classes.index(pos_label)
                            y_prob_pos = proba[:, idx]
                            y_true_bin = (pd.Series(y_test) == pos_label).astype(int)
                        else:
                            y_prob_pos = proba[:, 1] if proba.ndim == 2 else proba
                            y_true_bin = pd.Series(y_test).astype(int)

                        fpr, tpr, _ = roc_curve(y_true_bin, y_prob_pos)
                        roc_auc = auc(fpr, tpr)
                        fig_roc = go.Figure()
                        fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, name=f"AUC = {roc_auc:.2f}"))
                        fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', line=dict(dash='dash'), name='Random'))
                        fig_roc.update_layout(title="ROC Curve", xaxis_title="False Positive Rate", yaxis_title="True Positive Rate", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(apply_neuro_theme(fig_roc), use_container_width=True)
                    except Exception as e:
                        st.warning(f"ROC curve not available for this model: {e}")

                # Advanced details (leaderboard, classification report, baselines, tuning params, feature importance)
                with st.expander("Advanced Results (leaderboard, classification report, diagnostics)"):
                    try:
                        report = classification_report(y_test, y_pred, zero_division=0)
                        st.text_area("Classification Report", report, height=160)
                    except Exception:
                        pass

                    try:
                        leaderboard = pd.DataFrame(results)[['Model','Score']]
                        st.markdown('#### Leaderboard (models tried)')
                        st.table(leaderboard)
                    except Exception:
                        pass

                    # Baseline & Significance Checks
                    try:
                        st.markdown('### 🔬 Baseline & Significance Checks')
                        y_series = pd.Series(y_test)
                        majority_acc = y_series.value_counts(normalize=True).max()
                        n_classes = y_series.nunique()
                        random_acc = 1.0 / n_classes if n_classes > 0 else 0.0

                        try:
                            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
                            cv_scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy')
                            cv_mean = float(cv_scores.mean())
                        except Exception:
                            cv_mean = None

                        perm_pvalue = None
                        perm_score = None
                        try:
                            n_perms = 100 if len(X_test) > 50 else 300
                            score, perm_scores, pvalue = permutation_test_score(model, X_test, y_test, scoring='accuracy', n_permutations=min(n_perms, 500), random_state=42)
                            perm_score = float(score)
                            perm_pvalue = float(pvalue)
                        except Exception:
                            perm_pvalue = None
                            perm_score = None

                        c1, c2, c3 = st.columns(3)
                        with c1:
                            st.metric('Model Acc', f"{acc:.2%}")
                            if cv_mean is not None:
                                st.caption(f"CV Acc (5-fold): {cv_mean:.2%}")
                        with c2:
                            st.metric('Majority Baseline', f"{majority_acc:.2%}")
                            st.caption(f"Random Guess (uniform): {random_acc:.2%}")
                        with c3:
                            if perm_pvalue is not None:
                                st.metric('Perm p-value', f"{perm_pvalue:.4f}")
                                st.caption(f"Perm score: {perm_score:.2%}")
                            else:
                                st.caption('Permutation test unavailable')

                        margin = 0.02
                        if acc <= max(majority_acc, random_acc) + margin:
                            st.warning('Model performance is close to or worse than trivial baselines (majority/random).')
                        elif perm_pvalue is not None and perm_pvalue > 0.05:
                            st.warning('Permutation p-value > 0.05: model may not be significantly better than chance.')
                    except Exception:
                        pass

                    # Tuning params preview
                    try:
                        if enable_tuning_opt and 'best_params' in locals():
                            st.markdown('### Tuning Results (best_params)')
                            st.json(best_params)
                    except Exception:
                        pass

                    # Feature importance
                    try:
                        if hasattr(model, 'feature_importances_'):
                            st.subheader('Feature Importance')
                            fi = pd.DataFrame({'Feature': X.columns, 'Importance': model.feature_importances_}).sort_values(by='Importance', ascending=False)
                            st.bar_chart(fi.set_index('Feature'))
                    except Exception:
                        pass

            else:
                # Regression: keep previous metrics
                score = r2_score(y_test, y_pred)
                st.metric("R2 Score", f"{score:.4f}")

                # Compact regression summary and download
                try:
                    summary = {
                        'model': best_name if 'best_name' in locals() else type(model).__name__,
                        'r2': float(score)
                    }
                    s1, s2 = st.columns([3,1])
                    with s1:
                        st.markdown('#### Run Summary')
                        st.write(f"**Model:** {summary['model']}")
                        st.write(f"**R2:** {summary['r2']:.4f}")
                    with s2:
                        df_sum = pd.DataFrame([summary])
                        st.download_button('Download CSV', df_sum.to_csv(index=False), file_name='autonomous_summary_regression.csv', mime='text/csv')
                        st.download_button('Download JSON', df_sum.to_json(orient='records'), file_name='autonomous_summary_regression.json', mime='application/json')
                except Exception:
                    pass

                st.subheader("Model Insights")
                feature_importance = pd.DataFrame({
                    'Feature': X.columns,
                    'Importance': model.feature_importances_
                }).sort_values(by='Importance', ascending=False).head(10)
                st.bar_chart(feature_importance.set_index('Feature'))

            # Save to session
            st.session_state.model = model
            st.info("Model saved to session. You can now go to 'Model Deployment' to download it.")
            
        except Exception as e:
            st.error(f"Autonomous process failed: {e}")
