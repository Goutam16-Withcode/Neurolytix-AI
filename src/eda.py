import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from ui import section_header, apply_neuro_theme, clean_and_validate_data, coerce_single_column

# -----------------------------------------------------------------------------
# Modular Plotting Functions (DataPilot-AI Concept)
# -----------------------------------------------------------------------------

from visualization import (
    plot_numeric_distributions,
    plot_categorical_counts,
    plot_correlation_heatmap,
    plot_3d_scatter,
    display_figures_grid,
    render_plotly_with_fallback,
    create_matplotlib_histogram,
    create_matplotlib_boxplot,
    create_seaborn_plot,
)

# -----------------------------------------------------------------------------
# Main View Controller
# -----------------------------------------------------------------------------

def show_overview(df):
    section_header("Scientific Discovery Engine", "Advanced statistical profiling and 3D data mapping.")
    
    if df is None or df.empty:
        st.error("No data detected. Please load a dataset first.")
        return

    # 1. Cleaning Phase
    df_clean = clean_and_validate_data(df)

    # Quick check: if there are no numeric columns, present an explicit one-click coercion
    numeric_cols_quick = df_clean.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols_quick:
        st.warning("No numeric columns detected. Charts may not render. Try aggressive coercion to convert formatted numbers.")
        if st.button("One-Click Aggressive Coercion"):
            df_coerced = clean_and_validate_data(df, aggressive=True)
            st.session_state.df = df_coerced
            st.success("Aggressive coercion applied. Re-running EDA...")
            st.rerun()
    
    # Show coercion report and preview if present (helps debug why EDA charts might not render)
    report = st.session_state.get('_coercion_report', {})

    # Auto-coerce toggle (opt-in behavior)
    auto_coerce = st.checkbox("Auto-coerce formatted numbers when plots are missing (opt-in)", value=st.session_state.get('auto_coerce_on_missing', False), key='auto_coerce_opt_in')
    st.session_state['auto_coerce_on_missing'] = auto_coerce

    if report:
        coerced = report.get('aggressively_coerced', [])
        failed = report.get('aggressive_failed', [])
        if coerced or failed:
            msg = []
            if coerced:
                msg.append(f"Coerced: {', '.join(coerced)}")
            if failed:
                msg.append(f"Failed: {', '.join(failed)}")
            st.info("Numeric Coercion Report: " + " | ".join(msg))

        if 'preview' in report and report['preview']:
            with st.expander("Coercion Preview (before / after sample)"):
                rows = []
                for c, vv in report['preview'].items():
                    before = ", ".join([str(x) for x in vv.get('before', [])])
                    after = ", ".join([str(x) for x in vv.get('after', [])])
                    rows.append({'Column': c, 'Before sample': before, 'After sample': after, 'ColumnName': c})
                df_preview = pd.DataFrame(rows)
                st.dataframe(df_preview[['ColumnName','Before sample','After sample']].rename(columns={'ColumnName':'Column'}), use_container_width=True)

                # Per-column manual coercion buttons
                st.markdown("#### Manual Coercion")
                for c in df_preview['ColumnName'].tolist():
                    col1, col2 = st.columns([3,1])
                    with col1:
                        st.write(f"**{c}** — sample before/after shown above")
                    with col2:
                        if st.button(f"Coerce {c}", key=f"coerce_{c}"):
                            from ui import coerce_single_column
                            result = coerce_single_column(df, c)
                            if isinstance(result, bool) and not result:
                                st.warning(f"Could not coerce column {c}.")
                            else:
                                st.session_state.df = result
                                st.success(f"Coerced column {c}. Re-running EDA...")
                                st.rerun()

    # allow auto-coerce to run when plots would be missing
    if auto_coerce:
        # If currently no numeric columns and we haven't tried auto coercion yet, run it
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
        tried = st.session_state.get('_auto_coerce_tried', False)
        if (not numeric_cols) and (not tried):
            df_coerced = clean_and_validate_data(df, aggressive=True)
            st.session_state.df = df_coerced
            st.session_state['_auto_coerce_tried'] = True
            st.success("Auto coercion applied. Re-running EDA...")
            st.rerun()
    # Allow a force-rebuild operation to coerce numerics and show diagnostics
    if st.button("Force rebuild numeric columns and show diagnostics"):
        df_coerced = clean_and_validate_data(df, aggressive=True)
        st.session_state.df = df_coerced
        st.success("Rebuilt numeric columns and computed diagnostics. See diagnostics table below.")
        st.rerun()

    # Show diagnostics if available to explain why charts might not render
    diag = st.session_state.get('_coercion_diagnostics', {})
    if diag:
        diag_df = pd.DataFrame.from_dict(diag, orient='index').reset_index().rename(columns={'index': 'Column'})
        with st.expander("Numeric Coercion Diagnostics"):
            st.dataframe(diag_df.sort_values(by=['non_null_pct', 'unique'], ascending=[False, False]), use_container_width=True)
            # Highlight potential issues
            low_non_null = diag_df[diag_df['non_null_pct'] < 0.5]
            const_cols = diag_df[diag_df['is_constant']]
            if not low_non_null.empty:
                st.warning(f"Columns with <50% numeric values after coercion: {', '.join(low_non_null['Column'].tolist())}")
            if not const_cols.empty:
                st.info(f"Columns that are constant after coercion (no variance): {', '.join(const_cols['Column'].tolist())}")

    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df_clean.select_dtypes(include=['object', 'category']).columns.tolist()

    # 2. UI Layout
    eda_choice = st.radio(
        "Analysis Mode",
        ["Overview", "Categorical Analysis", "Advanced Analysis"],
        horizontal=True
    )
    
    st.markdown("---")

    # AutoViz features removed: data-quality and automated profiling tools have been removed.

    # (Auto-exclude / profile report functionality removed.)

    
    

    if eda_choice == "Overview":
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Rows", df.shape[0])
        col2.metric("Columns", df.shape[1])
        col3.metric("Numeric Features", len(numeric_cols))
        col4.metric("Categorical Features", len(categorical_cols))

        st.markdown("#### Data Sample")
        st.dataframe(df.head(10), use_container_width=True)

        if numeric_cols:
            st.markdown("#### Numeric Statistics")
            st.dataframe(df_clean[numeric_cols].describe(), use_container_width=True)

        if categorical_cols:
            st.markdown("#### Categorical Statistics")
            cat_stats = []
            for col in categorical_cols[:10]:  # Limit for performance
                value_counts = df_clean[col].value_counts()
                cat_stats.append({
                    'Column': col,
                    'Unique Values': len(value_counts),
                    'Most Common': value_counts.index[0] if len(value_counts) > 0 else 'N/A',
                    'Frequency': value_counts.iloc[0] if len(value_counts) > 0 else 0,
                    'Missing': df_clean[col].isnull().sum()
                })
            if cat_stats:
                st.dataframe(pd.DataFrame(cat_stats), use_container_width=True)

        # Quick visualizations
        st.markdown("#### Quick Overview Plots")

        # Distribution overview for numeric columns
        if numeric_cols:
            st.markdown("**Numeric Distributions**")
            figs = plot_numeric_distributions(df_clean, numeric_cols[:3])  # Show first 3
            for i, fig in enumerate(figs):
                col_name = numeric_cols[i] if i < len(numeric_cols) else f"Column {i+1}"
                render_plotly_with_fallback(fig, f"Overview: {col_name}", df=df_clean, plot_type="histogram", col=col_name)

        # Categorical overview
        if categorical_cols:
            st.markdown("**Categorical Distributions**")
            figs = plot_categorical_counts(df_clean, categorical_cols[:3])  # Show first 3
            cols = st.columns(2)
            for idx, fig in enumerate(figs):
                with cols[idx % 2]:
                    cat_name = categorical_cols[idx] if idx < len(categorical_cols) else f"Category {idx+1}"
                    render_plotly_with_fallback(fig, f"Categorical: {cat_name}")

        # Correlation heatmap overview
        if len(numeric_cols) >= 3:
            st.markdown("**Correlation Overview**")
            fig = plot_correlation_heatmap(df_clean, numeric_cols)
            render_plotly_with_fallback(fig, "Correlation Overview", df=df_clean, plot_type="heatmap")

    elif eda_choice == "Categorical Analysis":
        st.subheader("Categorical Frequencies")
        if categorical_cols:
            figs = plot_categorical_counts(df_clean, categorical_cols)
            cols = st.columns(2)
            for idx, fig in enumerate(figs):
                with cols[idx % 2]:
                    cat_name = categorical_cols[idx] if idx < len(categorical_cols) else f"Chart {idx+1}"
                    if not render_plotly_with_fallback(fig, f"Categorical: {cat_name}"):
                        st.warning(f"Could not generate categorical plot for {cat_name}")
        else:
            st.info("No categorical columns found.")

    elif eda_choice == "Advanced Analysis":
        st.subheader("Advanced Statistical Analysis & Insights")

        # Automated insights and statistical tests
        tab1, tab2, tab3, tab4 = st.tabs(["Data Quality", "Statistical Tests", "Outlier Analysis", "Automated Insights"])

        with tab1:
            st.markdown("### Data Quality Assessment")

            # Missing values analysis
            missing_data = df_clean.isnull().sum()
            missing_percent = (missing_data / len(df_clean)) * 100

            if missing_data.sum() > 0:
                st.warning(f"Found {missing_data.sum()} missing values across {len(missing_data[missing_data > 0])} columns")

                # Create missing values visualization
                missing_df = pd.DataFrame({
                    'Column': missing_data.index,
                    'Missing Count': missing_data.values,
                    'Missing %': missing_percent.values
                }).sort_values('Missing Count', ascending=False)

                missing_df = missing_df[missing_df['Missing Count'] > 0]

                fig = px.bar(missing_df, x='Column', y='Missing Count',
                           title='Missing Values by Column',
                           color='Missing %', color_continuous_scale='Reds')
                fig = apply_neuro_theme(fig)
                render_plotly_with_fallback(fig, "Missing Values Analysis")

                # Recommendations
                high_missing = missing_df[missing_df['Missing %'] > 50]
                if not high_missing.empty:
                    st.error(f"⚠️ High missing data in columns: {', '.join(high_missing['Column'].tolist())}")
                    st.info("Consider removing these columns or using advanced imputation techniques.")
            else:
                st.success("✅ No missing values detected!")

            # Data type distribution
            dtype_counts = df_clean.dtypes.value_counts()
            fig = px.pie(values=dtype_counts.values, names=dtype_counts.index.astype(str),
                        title='Data Type Distribution')
            fig = apply_neuro_theme(fig)
            render_plotly_with_fallback(fig, "Data Type Distribution")

        with tab2:
            st.markdown("### Statistical Tests & Normality")

            if numeric_cols:
                # Normality tests
                normality_results = []
                for col in numeric_cols[:5]:  # Limit to 5 for performance
                    series = df_clean[col].dropna()
                    if len(series) >= 3:
                        try:
                            from scipy import stats
                            _, p_value = stats.shapiro(series)
                            is_normal = p_value > 0.05
                            normality_results.append({
                                'Column': col,
                                'Normal': 'Yes' if is_normal else 'No',
                                'p-value': f"{p_value:.4f}",
                                'Sample Size': len(series)
                            })
                        except:
                            normality_results.append({
                                'Column': col,
                                'Normal': 'Test Failed',
                                'p-value': 'N/A',
                                'Sample Size': len(series)
                            })

                if normality_results:
                    normality_df = pd.DataFrame(normality_results)
                    st.dataframe(normality_df, use_container_width=True)

                    # Visualize normality with Q-Q plots for first few columns
                    cols = st.columns(2)
                    for i, col in enumerate(numeric_cols[:4]):
                        with cols[i % 2]:
                            try:
                                fig = px.scatter(x=stats.probplot(df_clean[col].dropna())[0][0],
                                               y=stats.probplot(df_clean[col].dropna())[0][1],
                                               title=f'Q-Q Plot: {col}')
                                fig.add_trace(go.Scatter(x=[-3, 3], y=[-3, 3], mode='lines',
                                                       line=dict(color='red', dash='dash'), name='Normal Line'))
                                fig = apply_neuro_theme(fig)
                                render_plotly_with_fallback(fig, f"Q-Q Plot: {col}")
                            except Exception as e:
                                st.error(f"Could not generate Q-Q plot for {col}: {str(e)}")

            # Correlation significance tests
            if len(numeric_cols) >= 2:
                st.markdown("#### Correlation Significance")
                corr_matrix = df_clean[numeric_cols].corr()

                # Find significant correlations
                significant_corr = []
                for i in range(len(numeric_cols)):
                    for j in range(i+1, len(numeric_cols)):
                        if not pd.isna(corr_matrix.iloc[i, j]):
                            try:
                                from scipy.stats import pearsonr
                                corr_val = corr_matrix.iloc[i, j]
                                _, p_val = pearsonr(df_clean[numeric_cols[i]].dropna(),
                                                  df_clean[numeric_cols[j]].dropna())
                                if p_val < 0.05:  # Significant at 95% confidence
                                    significant_corr.append({
                                        'Variable 1': numeric_cols[i],
                                        'Variable 2': numeric_cols[j],
                                        'Correlation': f"{corr_val:.3f}",
                                        'p-value': f"{p_val:.4f}",
                                        'Significance': 'Significant' if p_val < 0.05 else 'Not Significant'
                                    })
                            except:
                                continue

                if significant_corr:
                    corr_df = pd.DataFrame(significant_corr)
                    st.dataframe(corr_df, use_container_width=True)
                else:
                    st.info("No significant correlations found at 95% confidence level.")

        with tab3:
            st.markdown("### Outlier Analysis")

            if numeric_cols:
                outlier_summary = []
                for col in numeric_cols:
                    series = df_clean[col].dropna()
                    if len(series) > 0:
                        Q1 = series.quantile(0.25)
                        Q3 = series.quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR

                        outliers = series[(series < lower_bound) | (series > upper_bound)]
                        outlier_pct = len(outliers) / len(series) * 100

                        outlier_summary.append({
                            'Column': col,
                            'Outliers': len(outliers),
                            'Outlier %': f"{outlier_pct:.1f}%",
                            'Lower Bound': f"{lower_bound:.2f}",
                            'Upper Bound': f"{upper_bound:.2f}"
                        })

                outlier_df = pd.DataFrame(outlier_summary)
                st.dataframe(outlier_df, use_container_width=True)

                # Visualize outliers for selected column
                selected_col = st.selectbox("Select column for outlier visualization", numeric_cols)
                if selected_col:
                    series = df_clean[selected_col].dropna()
                    Q1 = series.quantile(0.25)
                    Q3 = series.quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR

                    # Create box plot with outliers highlighted
                    fig = go.Figure()
                    fig.add_trace(go.Box(y=series, name=selected_col,
                                       boxpoints='outliers', jitter=0.3, pointpos=-1.8))
                    fig.add_hline(y=lower_bound, line_dash="dash", line_color="red",
                                annotation_text="Lower Bound")
                    fig.add_hline(y=upper_bound, line_dash="dash", line_color="red",
                                annotation_text="Upper Bound")
                    fig.update_layout(title=f"Outlier Analysis: {selected_col}")
                    fig = apply_neuro_theme(fig)
                    render_plotly_with_fallback(fig, f"Outlier Analysis: {selected_col}")

        with tab4:
            st.markdown("### Automated Insights")

            insights = []

            # Basic insights
            insights.append(f"📊 Dataset contains {df_clean.shape[0]} rows and {df_clean.shape[1]} columns")
            insights.append(f"🔢 {len(numeric_cols)} numeric columns, {len(categorical_cols)} categorical columns")

            # Missing data insights
            missing_pct = (df_clean.isnull().sum().sum() / (df_clean.shape[0] * df_clean.shape[1])) * 100
            if missing_pct > 10:
                insights.append(f"⚠️ High missing data: {missing_pct:.1f}% of total cells are missing")
            elif missing_pct > 0:
                insights.append(f"ℹ️ {missing_pct:.1f}% of data is missing - generally acceptable")

            # Correlation insights
            if len(numeric_cols) >= 2:
                corr_matrix = df_clean[numeric_cols].corr()
                strong_corr = []
                for i in range(len(numeric_cols)):
                    for j in range(i+1, len(numeric_cols)):
                        if abs(corr_matrix.iloc[i, j]) > 0.7:
                            strong_corr.append(f"{numeric_cols[i]} & {numeric_cols[j]} (r={corr_matrix.iloc[i, j]:.2f})")

                if strong_corr:
                    insights.append(f"🔗 Strong correlations found: {', '.join(strong_corr[:3])}")
                    if len(strong_corr) > 3:
                        insights.append(f"   ... and {len(strong_corr) - 3} more strong correlations")

            # Outlier insights
            if numeric_cols:
                total_outliers = 0
                for col in numeric_cols:
                    series = df_clean[col].dropna()
                    if len(series) > 0:
                        Q1, Q3 = series.quantile([0.25, 0.75])
                        IQR = Q3 - Q1
                        outliers = series[(series < Q1 - 1.5*IQR) | (series > Q3 + 1.5*IQR)]
                        total_outliers += len(outliers)

                outlier_pct = total_outliers / df_clean.shape[0] * 100
                if outlier_pct > 5:
                    insights.append(f"⚠️ {total_outliers} outliers detected ({outlier_pct:.1f}% of rows) - consider outlier treatment")

            # Data type insights
            if len(categorical_cols) > 0:
                avg_categories = sum(len(df_clean[col].unique()) for col in categorical_cols) / len(categorical_cols)
                insights.append(f"📋 Categorical variables have average {avg_categories:.1f} unique values each")

            # Display insights
            for insight in insights:
                st.info(insight)

            # Recommendations
            st.markdown("### 🤖 AI Recommendations")

            recommendations = []

            if missing_pct > 20:
                recommendations.append("Consider advanced imputation techniques or removing columns with high missing data")

            if len(numeric_cols) >= 3 and len(strong_corr) > 0:
                recommendations.append("Strong correlations detected - consider dimensionality reduction techniques like PCA")

            if outlier_pct > 10:
                recommendations.append("High outlier presence - consider robust statistical methods or outlier removal")

            if len(categorical_cols) > 0 and avg_categories > 10:
                recommendations.append("High cardinality categorical variables detected - consider encoding techniques")

            if len(numeric_cols) < 3:
                recommendations.append("Limited numeric features - consider feature engineering")

            if recommendations:
                for rec in recommendations:
                    st.success(f"💡 {rec}")
            else:
                st.success("✅ Dataset looks well-structured for analysis!")


