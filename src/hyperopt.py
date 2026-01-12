import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC, SVR
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
import optuna
from ui import section_header
import time

def show_hyperparameter_optimization(df):
    section_header("Hyperparameter Optimization", "Optimize model hyperparameters using Grid Search, Random Search, and Bayesian Optimization.")

    if df is None:
        st.error("Please load a dataset first.")
        return

    # Problem type detection
    target_col = st.selectbox("Select Target Column", df.columns)
    if target_col:
        target_values = df[target_col].dropna()
        if target_values.dtype == 'object' or len(target_values.unique()) < 20:
            problem_type = "classification"
            st.info(f"Detected **{problem_type}** problem with {len(target_values.unique())} classes.")
        else:
            problem_type = "regression"
            st.info(f"Detected **{problem_type}** problem.")

        # Algorithm selection
        if problem_type == "classification":
            algorithms = {
                "Random Forest": RandomForestClassifier(),
                "Logistic Regression": LogisticRegression(max_iter=1000),
                "SVM": SVC()
            }
        else:
            algorithms = {
                "Random Forest": RandomForestRegressor(),
                "Linear Regression": LinearRegression(),
                "SVM": SVR()
            }

        algorithm = st.selectbox("Select Algorithm", list(algorithms.keys()))

        # Optimization method
        opt_method = st.selectbox("Optimization Method",
                                ["Grid Search", "Random Search", "Bayesian Optimization (Optuna)"])

        if st.button("Start Hyperparameter Optimization"):
            with st.spinner("Optimizing hyperparameters..."):
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

                # Perform optimization based on method
                if opt_method == "Grid Search":
                    results = perform_grid_search(X_train, y_train, algorithms[algorithm], problem_type)
                elif opt_method == "Random Search":
                    results = perform_random_search(X_train, y_train, algorithms[algorithm], problem_type)
                else:  # Bayesian Optimization
                    results = perform_bayesian_opt(X_train, y_train, algorithm, problem_type)

                # Display results
                display_optimization_results(results, X_test, y_test, problem_type)

def perform_grid_search(X_train, y_train, model, problem_type):
    """Perform Grid Search hyperparameter optimization."""
    start_time = time.time()

    if isinstance(model, RandomForestClassifier) or isinstance(model, RandomForestRegressor):
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20, 30],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
    elif isinstance(model, LogisticRegression) or isinstance(model, LinearRegression):
        param_grid = {
            'C': [0.1, 1, 10, 100] if isinstance(model, LogisticRegression) else [],
            'penalty': ['l1', 'l2'] if isinstance(model, LogisticRegression) else [],
            'solver': ['liblinear', 'saga'] if isinstance(model, LogisticRegression) else []
        }
        if not param_grid['C']:  # For LinearRegression
            param_grid = {'fit_intercept': [True, False]}
    else:  # SVM
        param_grid = {
            'C': [0.1, 1, 10, 100],
            'kernel': ['rbf', 'linear', 'poly'],
            'gamma': ['scale', 'auto', 0.001, 0.01, 0.1, 1]
        }

    grid_search = GridSearchCV(model, param_grid, cv=3, scoring='accuracy' if problem_type == 'classification' else 'neg_mean_squared_error', n_jobs=-1)
    grid_search.fit(X_train, y_train)

    execution_time = time.time() - start_time

    return {
        'method': 'Grid Search',
        'best_params': grid_search.best_params_,
        'best_score': grid_search.best_score_,
        'execution_time': execution_time,
        'cv_results': grid_search.cv_results_,
        'best_estimator': grid_search.best_estimator_
    }

def perform_random_search(X_train, y_train, model, problem_type):
    """Perform Random Search hyperparameter optimization."""
    start_time = time.time()

    if isinstance(model, RandomForestClassifier) or isinstance(model, RandomForestRegressor):
        param_dist = {
            'n_estimators': [50, 100, 150, 200, 250],
            'max_depth': [None, 10, 20, 30, 40, 50],
            'min_samples_split': [2, 5, 10, 15],
            'min_samples_leaf': [1, 2, 4, 6],
            'max_features': ['auto', 'sqrt', 'log2']
        }
    elif isinstance(model, LogisticRegression) or isinstance(model, LinearRegression):
        param_dist = {
            'C': np.logspace(-4, 4, 20) if isinstance(model, LogisticRegression) else [],
            'penalty': ['l1', 'l2'] if isinstance(model, LogisticRegression) else [],
            'solver': ['liblinear', 'saga'] if isinstance(model, LogisticRegression) else []
        }
        if not param_dist['C']:  # For LinearRegression
            param_dist = {'fit_intercept': [True, False]}
    else:  # SVM
        param_dist = {
            'C': np.logspace(-3, 3, 7),
            'kernel': ['rbf', 'linear', 'poly', 'sigmoid'],
            'gamma': np.logspace(-3, 1, 5),
            'degree': [2, 3, 4] if hasattr(model, 'degree') else []
        }

    random_search = RandomizedSearchCV(model, param_dist, n_iter=20, cv=3,
                                     scoring='accuracy' if problem_type == 'classification' else 'neg_mean_squared_error',
                                     n_jobs=-1, random_state=42)
    random_search.fit(X_train, y_train)

    execution_time = time.time() - start_time

    return {
        'method': 'Random Search',
        'best_params': random_search.best_params_,
        'best_score': random_search.best_score_,
        'execution_time': execution_time,
        'cv_results': random_search.cv_results_,
        'best_estimator': random_search.best_estimator_
    }

def perform_bayesian_opt(X_train, y_train, algorithm, problem_type):
    """Perform Bayesian Optimization using Optuna."""
    start_time = time.time()

    def objective(trial):
        if algorithm == "Random Forest":
            if problem_type == "classification":
                model = RandomForestClassifier(
                    n_estimators=trial.suggest_int('n_estimators', 50, 300),
                    max_depth=trial.suggest_int('max_depth', 3, 50),
                    min_samples_split=trial.suggest_int('min_samples_split', 2, 20),
                    min_samples_leaf=trial.suggest_int('min_samples_leaf', 1, 10),
                    random_state=42
                )
            else:
                model = RandomForestRegressor(
                    n_estimators=trial.suggest_int('n_estimators', 50, 300),
                    max_depth=trial.suggest_int('max_depth', 3, 50),
                    min_samples_split=trial.suggest_int('min_samples_split', 2, 20),
                    min_samples_leaf=trial.suggest_int('min_samples_leaf', 1, 10),
                    random_state=42
                )
        elif algorithm == "Logistic Regression":
            model = LogisticRegression(
                C=trial.suggest_float('C', 1e-4, 1e4, log=True),
                penalty=trial.suggest_categorical('penalty', ['l1', 'l2']),
                solver='liblinear',
                max_iter=1000,
                random_state=42
            )
        elif algorithm == "SVM":
            if problem_type == "classification":
                model = SVC(
                    C=trial.suggest_float('C', 1e-3, 1e3, log=True),
                    kernel=trial.suggest_categorical('kernel', ['rbf', 'linear', 'poly']),
                    gamma=trial.suggest_float('gamma', 1e-3, 1e1, log=True),
                    random_state=42
                )
            else:
                model = SVR(
                    C=trial.suggest_float('C', 1e-3, 1e3, log=True),
                    kernel=trial.suggest_categorical('kernel', ['rbf', 'linear', 'poly']),
                    gamma=trial.suggest_float('gamma', 1e-3, 1e1, log=True)
                )
        else:
            # Default fallback
            model = RandomForestClassifier(n_estimators=100, random_state=42) if problem_type == "classification" else RandomForestRegressor(n_estimators=100, random_state=42)

        # Cross-validation score
        from sklearn.model_selection import cross_val_score
        scores = cross_val_score(model, X_train, y_train, cv=3, scoring='accuracy' if problem_type == 'classification' else 'neg_mean_squared_error')
        return scores.mean() if problem_type == 'classification' else -scores.mean()

    study = optuna.create_study(direction='maximize' if problem_type == 'classification' else 'minimize')
    study.optimize(objective, n_trials=20, timeout=300)  # 5 minute timeout

    execution_time = time.time() - start_time

    # Train best model
    best_params = study.best_params
    if algorithm == "Random Forest":
        if problem_type == "classification":
            best_model = RandomForestClassifier(**best_params, random_state=42)
        else:
            best_model = RandomForestRegressor(**best_params, random_state=42)
    elif algorithm == "Logistic Regression":
        best_model = LogisticRegression(**best_params, solver='liblinear', max_iter=1000, random_state=42)
    elif algorithm == "SVM":
        if problem_type == "classification":
            best_model = SVC(**best_params, random_state=42)
        else:
            best_model = SVR(**best_params)
    else:
        best_model = RandomForestClassifier(n_estimators=100, random_state=42) if problem_type == "classification" else RandomForestRegressor(n_estimators=100, random_state=42)

    best_model.fit(X_train, y_train)

    return {
        'method': 'Bayesian Optimization (Optuna)',
        'best_params': study.best_params,
        'best_score': study.best_value,
        'execution_time': execution_time,
        'study': study,
        'best_estimator': best_model
    }

def display_optimization_results(results, X_test, y_test, problem_type):
    """Display the optimization results."""
    st.success("Hyperparameter optimization completed!")

    # Best parameters
    st.subheader("🎯 Best Hyperparameters Found")
    st.json(results['best_params'])

    # Performance metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Best CV Score", f"{results['best_score']:.4f}")
    with col2:
        st.metric("Execution Time", f"{results['execution_time']:.2f}s")
    with col3:
        # Test set performance
        y_pred = results['best_estimator'].predict(X_test)
        if problem_type == "classification":
            test_score = accuracy_score(y_test, y_pred)
            st.metric("Test Accuracy", f"{test_score:.4f}")
        else:
            test_score = r2_score(y_test, y_pred)
            st.metric("Test R² Score", f"{test_score:.4f}")

    # Method-specific results
    if results['method'] == 'Bayesian Optimization (Optuna)':
        st.subheader("📊 Optimization History")
        fig = optuna.visualization.plot_optimization_history(results['study'])
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🔍 Parameter Importance")
        fig = optuna.visualization.plot_param_importances(results['study'])
        st.plotly_chart(fig, use_container_width=True)

    elif 'cv_results' in results:
        st.subheader("📈 Cross-Validation Results")
        cv_df = pd.DataFrame(results['cv_results'])
        if 'mean_test_score' in cv_df.columns:
            st.line_chart(cv_df['mean_test_score'])

    # Feature importance (if available)
    if hasattr(results['best_estimator'], 'feature_importances_'):
        st.subheader("🌟 Feature Importance")
        feature_importance = pd.DataFrame({
            'feature': X_test.columns,
            'importance': results['best_estimator'].feature_importances_
        }).sort_values('importance', ascending=False)

        st.bar_chart(feature_importance.set_index('feature'))

    # Model export
    st.subheader("💾 Export Optimized Model")
    import joblib
    import base64

    model_buffer = joblib.dumps(results['best_estimator'])
    b64_model = base64.b64encode(model_buffer).decode()

    st.download_button(
        label="Download Model (Joblib)",
        data=model_buffer,
        file_name="optimized_model.joblib",
        mime="application/octet-stream"
    )

    # Summary
    st.subheader("📋 Optimization Summary")
    summary = f"""
    **Method:** {results['method']}
    **Best Score:** {results['best_score']:.4f}
    **Execution Time:** {results['execution_time']:.2f} seconds
    **Parameters Optimized:** {len(results['best_params'])}
    """
    st.info(summary)