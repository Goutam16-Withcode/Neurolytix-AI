import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from ui import section_header, apply_neuro_theme, clean_and_validate_data

# Alternative rendering functions for when plotly fails
def render_plotly_with_fallback(fig, title="Chart", use_container_width=True, df=None, plot_type="auto", **kwargs):
    """Render plotly chart with matplotlib fallback"""
    try:
        if fig is not None:
            st.plotly_chart(fig, use_container_width=use_container_width)
            return True
        else:
            st.warning(f"Could not generate {title} - no data available")
            return False
    except Exception as e:
        st.warning(f"Plotly rendering failed for {title}: {str(e)}")
        st.info("Trying alternative matplotlib rendering...")

        # Try matplotlib fallback
        try:
            if df is not None and plot_type != "auto":
                if plot_type == "histogram" and "col" in kwargs:
                    fig_fallback = create_matplotlib_histogram(df, kwargs["col"], title)
                    if fig_fallback:
                        st.pyplot(fig_fallback)
                        st.info(f"Showing matplotlib {plot_type} as plotly failed")
                        return True
                elif plot_type == "heatmap":
                    fig_fallback = create_seaborn_plot(df, "heatmap")
                    if fig_fallback:
                        st.pyplot(fig_fallback)
                        st.info("Showing seaborn heatmap as plotly failed")
                        return True

            st.error(f"Could not generate any visualization for {title}")
            return False

        except Exception as fallback_e:
            st.error(f"Both plotly and matplotlib rendering failed for {title}: {str(fallback_e)}")
            return False

def create_matplotlib_scatter(df, x_col, y_col, title="Scatter Plot"):
    """Create matplotlib scatter plot as fallback"""
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(df[x_col], df[y_col], alpha=0.6, color='#00d2ff', edgecolors='white', linewidth=0.5)
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(title, color='#00d2ff', fontsize=14)
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('#1a1a2e')
        fig.patch.set_facecolor('#1a1a2e')
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('#00d2ff')
        return fig
    except Exception as e:
        st.error(f"Matplotlib scatter plot also failed: {str(e)}")
        return None

def create_matplotlib_histogram(df, col, title="Histogram"):
    """Create matplotlib histogram as fallback"""
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(df[col].dropna(), bins=30, alpha=0.7, color='#00d2ff', edgecolor='white')
        ax.set_xlabel(col)
        ax.set_ylabel('Frequency')
        ax.set_title(title, color='#00d2ff', fontsize=14)
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('#1a1a2e')
        fig.patch.set_facecolor('#1a1a2e')
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('#00d2ff')
        return fig
    except Exception as e:
        st.error(f"Matplotlib histogram also failed: {str(e)}")
        return None

def create_matplotlib_boxplot(df, x_col, y_col, title="Box Plot"):
    """Create matplotlib box plot as fallback"""
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        # Prepare data for boxplot
        if x_col != y_col:
            data = [df[df[x_col] == val][y_col].dropna() for val in df[x_col].unique()[:10]]
            labels = list(df[x_col].unique()[:10])
        else:
            data = [df[y_col].dropna()]
            labels = [y_col]

        if data:
            bp = ax.boxplot(data, labels=labels, patch_artist=True)
            for patch in bp['boxes']:
                patch.set_facecolor('#00d2ff')
                patch.set_alpha(0.7)
            ax.set_title(title, color='#00d2ff', fontsize=14)
            ax.grid(True, alpha=0.3)
            ax.set_facecolor('#1a1a2e')
            fig.patch.set_facecolor('#1a1a2e')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('#00d2ff')
            return fig
        return None
    except Exception as e:
        st.error(f"Matplotlib box plot also failed: {str(e)}")
        return None


def _make_columns_unique(df):
    """Return a copy of df with unique column names and a mapping of duplicates.
    If a column name appears multiple times, suffixes like '__1', '__2' are added.
    """
    cols = list(df.columns)
    seen = {}
    new_cols = []
    duplicates = {}
    for c in cols:
        if c in seen:
            seen[c] += 1
            new_name = f"{c}__{seen[c]}"
            duplicates.setdefault(c, []).append(new_name)
        else:
            seen[c] = 0
            new_name = c
        new_cols.append(new_name)
    if any(count > 0 for count in seen.values()):
        df2 = df.copy()
        df2.columns = new_cols
        return df2, duplicates
    return df, {}


# Palettes and plotting helpers (distinct palettes per chart type)
PALETTES = {
    'histogram': ['#1f77b4'],    # blue
    'bar': ['#ff7f0e'],          # orange
    'scatter': ['#00cc96'],      # green
    'scatter3d': ['#9467bd'],    # purple
    'heatmap': 'Viridis',
    'correlation': 'RdBu'
}


def get_color_sequence(chart_type):
    # Return a single string for solid colors, or list/scale for others
    palette = PALETTES.get(chart_type, '#00d2ff')
    if isinstance(palette, list) and len(palette) == 1:
        return palette[0]
    return palette


def plot_numeric_distributions(df, numeric_cols, max_cols=6):
    figs = []
    for col in numeric_cols[:max_cols]:
        s = df[col].dropna()
        if s.empty:
            continue

        # Create subplot with histogram, box plot, and violin plot
        from plotly.subplots import make_subplots
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Histogram with KDE', 'Box Plot', 'Violin Plot'),
            shared_xaxes=True,
            vertical_spacing=0.1
        )

        # Histogram
        fig.add_trace(go.Histogram(
            x=s,
            nbinsx=30,
            name='Histogram',
            marker_color=get_color_sequence('histogram'),
            opacity=0.7,
            showlegend=False
        ), row=1, col=1)

        # Add KDE-like density curve
        from scipy import stats
        try:
            kde_x = np.linspace(s.min(), s.max(), 100)
            kde_y = stats.gaussian_kde(s)(kde_x)
            # Scale KDE to match histogram
            hist_max = np.histogram(s, bins=30)[0].max()
            kde_y_scaled = kde_y * hist_max / kde_y.max()

            fig.add_trace(go.Scatter(
                x=kde_x,
                y=kde_y_scaled,
                mode='lines',
                name='Density',
                line=dict(color='#00d2ff', width=3),
                showlegend=False
            ), row=1, col=1)
        except:
            pass  # Skip KDE if scipy fails

        # Box Plot
        fig.add_trace(go.Box(
            x=s,
            name='Box Plot',
            marker_color=get_color_sequence('bar'),
            showlegend=False
        ), row=2, col=1)

        # Violin Plot
        fig.add_trace(go.Violin(
            x=s,
            name='Violin Plot',
            marker_color=get_color_sequence('scatter'),
            showlegend=False,
            box_visible=True,
            meanline_visible=True
        ), row=3, col=1)

        # Add statistics annotations to histogram
        mean_val = s.mean()
        median_val = s.median()
        std_val = s.std()

        # Note: vlines on subplots may cause rendering issues, using title instead

        fig.update_layout(
            title=f"Distribution Analysis: {col}<br><sub>Mean: {mean_val:.2f} | Median: {median_val:.2f} | Std: {std_val:.2f}</sub>",
            height=600,
            bargap=0.1
        )
        figs.append(apply_neuro_theme(fig))
    return figs


def plot_categorical_counts(df, categorical_cols, max_cols=6):
    figs = []
    for col in categorical_cols[:max_cols]:
        vc = df[col].value_counts().head(15)  # Show more categories
        if vc.empty:
            continue

        # Create enhanced bar chart with percentages
        total = vc.sum()
        percentages = (vc / total * 100).round(1)

        fig = go.Figure()

        # Add bars
        fig.add_trace(go.Bar(
            x=vc.values,
            y=vc.index.astype(str),
            orientation='h',
            marker_color=get_color_sequence('bar'),
            opacity=0.8,
            text=[f"{val} ({pct}%)" for val, pct in zip(vc.values, percentages)],
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Count: %{x}<br>Percentage: %{text}<extra></extra>'
        ))

        # Add percentage annotations
        for i, (val, pct) in enumerate(zip(vc.values, percentages)):
            fig.add_annotation(
                x=val + max(vc.values) * 0.02,
                y=vc.index[i],
                text=f"{pct}%",
                showarrow=False,
                font=dict(size=10, color='rgba(255,255,255,0.8)'),
                xanchor='left',
                yanchor='middle'
            )

        fig.update_layout(
            title=f"Top Categories: {col}<br><sub>Total: {total} | Unique: {len(vc)}</sub>",
            height=max(400, len(vc) * 25),
            xaxis_title="Count",
            yaxis_title="Category",
            bargap=0.1
        )
        figs.append(apply_neuro_theme(fig))
    return figs


def plot_correlation_heatmap(df, numeric_cols):
    if len(numeric_cols) < 2:
        return None

    # Calculate correlation matrix
    corr = df[numeric_cols].corr()

    # Create enhanced heatmap with annotations
    fig = go.Figure()

    # Determine validation settings based on number of columns
    n_cols = len(numeric_cols)
    show_text = n_cols <= 20
    
    # Add heatmap
    fig.add_trace(go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.index,
        colorscale=get_color_sequence('correlation'),
        text=np.round(corr.values, 2) if show_text else None,
        texttemplate='%{text}' if show_text else None,
        textfont={"size": 10},
        hoverongaps=False,
        hovertemplate='<b>%{x} vs %{y}</b><br>Correlation: %{z:.3f}<extra></extra>'
    ))

    # Add correlation strength indicators
    annotations = []
    if show_text:
        for i, row in enumerate(corr.index):
            for j, col in enumerate(corr.columns):
                if i != j:  # Skip diagonal
                    corr_val = corr.iloc[i, j]
                    strength = "Strong" if abs(corr_val) > 0.7 else "Moderate" if abs(corr_val) > 0.3 else "Weak"
                    direction = "Positive" if corr_val > 0 else "Negative"
                    annotations.append(f"{row} ↔ {col}: {strength} {direction} ({corr_val:.2f})")
    
    # Add summary annotation
    strong_corr = [(i, j, corr.iloc[i, j]) for i in range(len(corr)) for j in range(i+1, len(corr))
                   if abs(corr.iloc[i, j]) > 0.7]

    summary_text = f"Strong correlations found: {len(strong_corr)}"
    if strong_corr:
        summary_text += "<br>" + "<br>".join([f"• {corr.index[i]} & {corr.columns[j]}: {val:.2f}"
                                             for i, j, val in strong_corr[:3]])

    fig.update_layout(
        title=f'Feature Correlation Matrix<br><sub>{summary_text}</sub>',
        height=max(600, n_cols * 50),
        xaxis=dict(side='bottom', tickangle=-45),
        yaxis=dict(autorange='reversed')
    )

    return apply_neuro_theme(fig)


def plot_3d_scatter(df, x, y, z, color_by=None):
    if df is None or x not in df.columns or y not in df.columns or z not in df.columns:
        return None
    
    # Plotly handles NaN values gracefully, so no need for dropna
    cols = [x, y, z]
    if color_by: cols.append(color_by)

    # Check if there's any data at all
    data_check = df[cols].notna().any().any()
    if not data_check:
        return None
        
    if color_by and color_by in df.columns:
        fig = px.scatter_3d(df, x=x, y=y, z=z, color=color_by, opacity=0.8)
    else:
        fig = px.scatter_3d(df, x=x, y=y, z=z, opacity=0.8)
        fig.update_traces(marker_color=get_color_sequence('scatter3d'))
        
    fig.update_layout(height=650, title={'x':0.02})
    return apply_neuro_theme(fig)


def display_figures_grid(figs, cols=2):
    if not figs:
        return
    c = st.columns(cols)
    for idx, fig in enumerate(figs):
        with c[idx % cols]:
            st.plotly_chart(fig, use_container_width=True)


def render_single(fig):
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)


# Seaborn plotting functions for enhanced visualizations
def create_seaborn_plot(df, plot_type, **kwargs):
    """Create seaborn plots with matplotlib backend"""
    # Set seaborn style for dark theme
    sns.set_style("darkgrid", {
        "axes.facecolor": "#1a1a2e",
        "figure.facecolor": "#1a1a2e",
        "grid.color": "#2a2a4e",
        "axes.edgecolor": "#2a2a4e",
        "axes.labelcolor": "#e0e0e0",
        "xtick.color": "#b0b0b0",
        "ytick.color": "#b0b0b0",
        "text.color": "#e0e0e0"
    })

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')

    try:
        if plot_type == "pairplot":
            # Create pairplot for ALL numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) >= 2:
                # For large datasets, limit to prevent performance issues
                max_cols = min(len(numeric_cols), 10)  # Allow up to 10 columns
                selected_cols = numeric_cols[:max_cols]

                if len(selected_cols) < len(numeric_cols):
                    st.info(f"Showing pairplot for first {max_cols} numeric columns out of {len(numeric_cols)} total. Use individual scatter plots for more detailed analysis.")

                pair_plot = sns.pairplot(df[selected_cols], diag_kind='kde', plot_kws={'alpha': 0.6})
                pair_plot.fig.suptitle(f"Pairwise Relationships ({len(selected_cols)} variables)", y=1.02, color='#00d2ff', fontsize=16)
                return pair_plot.fig
            else:
                return None

        elif plot_type == "heatmap":
            # Correlation heatmap with seaborn
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            n_cols = len(numeric_cols)
            if n_cols >= 2:
                corr = df[numeric_cols].corr()
                mask = np.triu(np.ones_like(corr, dtype=bool))
                
                # Dynamic adjustment
                annot = n_cols <= 20
                if n_cols > 15:
                    new_size = max(10, n_cols * 0.5)
                    fig.set_size_inches(new_size, new_size * 0.8)
                
                sns.heatmap(corr, mask=mask, annot=annot, cmap='coolwarm', center=0,
                           square=True, linewidths=.5, ax=ax, fmt='.2f',
                           cbar_kws={"shrink": .8})
                ax.set_title("Correlation Heatmap", color='#00d2ff', fontsize=14, pad=20)
                return fig
            else:
                return None

        elif plot_type == "boxplot":
            # Box plot for categorical vs numeric
            cat_col = kwargs.get('cat_col')
            num_col = kwargs.get('num_col')
            if cat_col and num_col and cat_col in df.columns and num_col in df.columns:
                # Check if there's any data at all
                data_check = df[[cat_col, num_col]].notna().any().any()
                if data_check:
                    # Limit to top 10 categories
                    top_cats = df[cat_col].value_counts().head(10).index
                    subset_filtered = df[df[cat_col].isin(top_cats)]

                    sns.boxplot(data=subset_filtered, x=cat_col, y=num_col, ax=ax,
                               palette='husl', width=0.6)
                    ax.set_title(f"Box Plot: {num_col} by {cat_col}", color='#00d2ff', fontsize=14)
                    ax.tick_params(axis='x', rotation=45)
                    return fig
            return None

        elif plot_type == "violinplot":
            # Violin plot
            cat_col = kwargs.get('cat_col')
            num_col = kwargs.get('num_col')
            if cat_col and num_col and cat_col in df.columns and num_col in df.columns:
                # Check if there's any data at all
                data_check = df[[cat_col, num_col]].notna().any().any()
                if data_check:
                    top_cats = df[cat_col].value_counts().head(8).index
                    subset_filtered = df[df[cat_col].isin(top_cats)]

                    sns.violinplot(data=subset_filtered, x=cat_col, y=num_col, ax=ax,
                                  palette='husl', inner='quartile')
                    ax.set_title(f"Violin Plot: {num_col} by {cat_col}", color='#00d2ff', fontsize=14)
                    ax.tick_params(axis='x', rotation=45)
                    return fig
            return None

        elif plot_type == "scatterplot":
            # Enhanced scatter plot with regression line
            x_col = kwargs.get('x_col')
            y_col = kwargs.get('y_col')
            hue_col = kwargs.get('hue_col')

            if x_col and y_col and x_col in df.columns and y_col in df.columns:
                # Check if there's any data at all
                cols_to_check = [x_col, y_col]
                if hue_col and hue_col in df.columns and hue_col != 'None':
                    cols_to_check.append(hue_col)
                data_check = df[cols_to_check].notna().any().any()
                if data_check:
                    if hue_col and hue_col != 'None' and hue_col in df.columns:
                        sns.scatterplot(data=df, x=x_col, y=y_col, hue=hue_col,
                                       ax=ax, alpha=0.7, palette='husl')
                        # Add regression line for each hue group - limit to avoid too many lines
                        unique_hues = df[hue_col].dropna().unique()[:5]  # Limit to 5 groups
                        for hue_val in unique_hues:
                            group_data = df[df[hue_col] == hue_val]
                            if len(group_data) > 2:
                                sns.regplot(data=group_data, x=x_col, y=y_col,
                                           scatter=False, ax=ax, ci=None, line_kws={'alpha': 0.8})
                    else:
                        sns.scatterplot(data=df, x=x_col, y=y_col, ax=ax,
                                       alpha=0.7, color='#00d2ff')
                        sns.regplot(data=df, x=x_col, y=y_col, scatter=False,
                                   ax=ax, color='#ff6b6b', line_kws={'linewidth': 2})

                    ax.set_title(f"Scatter Plot: {y_col} vs {x_col}", color='#00d2ff', fontsize=14)
                    ax.grid(True, alpha=0.3)
                    return fig
            return None

    except Exception as e:
        st.warning(f"Error creating seaborn plot: {e}")
        return None

    return None


# Removed local apply_theme, now using ui.apply_neuro_theme

def show_visualization(df):
    section_header("Visual Analytics", "Explore relationships and patterns in your data.")

    if df is None:
        st.error("No DataFrame provided.")
        return

    # 1. Cleaning Phase (Centralized)
    df = clean_and_validate_data(df)

    if df.empty:
        st.error("DataFrame is empty after cleaning.")
        return

    # Ensure column names are unique before showing charts (Plotly requires unique names)
    df, duplicates = _make_columns_unique(df)
    if duplicates:
        dup_msg = ", ".join([f"{orig} -> {', '.join(new)}" for orig, new in duplicates.items()])
        st.warning(f"Duplicate column names detected and renamed: {dup_msg}")
        st.info("Tip: Clean or rename duplicate columns in your dataset to avoid auto-renaming.")
    
    # Add visualization library selector
    viz_library = st.radio("Visualization Library", ["Plotly (Interactive)", "Seaborn (Statistical)"], horizontal=True)

    if viz_library == "Plotly (Interactive)":
        chart_type = st.selectbox("Select Chart Type", [
            "Scatter Plot", "Bar Chart", "Line Chart", "Histogram",
            "Box Plot", "Violin Plot", "Area Chart", "Pie Chart", "Sunburst Chart", "Heatmap"
        ])
    else:  # Seaborn
        chart_type = st.selectbox("Select Chart Type", [
            "Pair Plot", "Correlation Heatmap", "Box Plot", "Violin Plot", "Scatter Plot"
        ])

    columns = df.columns.tolist()
    
    # ... (Keep existing scatter logic if needed, or replace/merge)
    
    if chart_type == "Scatter Plot":
        x_col = st.selectbox("X Axis", columns)
        y_col = st.selectbox("Y Axis", columns, index=1 if len(columns) > 1 else 0)
        hue_col = st.selectbox("Color (Hue)", ["None"] + columns)

        # Prevent duplicate column names when selecting the same field for both axes
        if x_col == y_col:
            st.warning("X and Y axes are the same column — pick different columns or use one of them against the index for meaningful visualization.")
        else:
            # Plotly handles NaN values gracefully, so no need for dropna
            cols_needed = [x_col, y_col]
            color = hue_col if hue_col != "None" else None
            if color and color not in cols_needed:
                cols_needed.append(color)

            # Check if there's any data at all
            data_check = df[cols_needed].notna().any().any()
            if not data_check:
                st.warning(f"No data available for {', '.join(cols_needed)} - all values are null.")
            else:
                if color is None:
                    fig = px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}", opacity=0.7)
                    fig.update_traces(
                        marker_color=get_color_sequence('scatter'),
                        marker_line_color='rgba(255, 255, 255, 0.2)',
                        marker_line_width=1,
                        marker_size=10
                    )
                else:
                    fig = px.scatter(df, x=x_col, y=y_col, color=color, title=f"{y_col} vs {x_col}", opacity=0.7)
                    fig.update_traces(
                        marker_line_color='rgba(255, 255, 255, 0.2)',
                        marker_line_width=1,
                        marker_size=10
                    )
                fig.update_layout(height=520)
                if not render_plotly_with_fallback(apply_neuro_theme(fig), "Scatter Plot"):
                    # Try matplotlib scatter as fallback
                    fig_mpl = create_matplotlib_scatter(df, x_col, y_col, f"Scatter Plot: {y_col} vs {x_col}")
                    if fig_mpl:
                        st.pyplot(fig_mpl) 
            
    elif chart_type == "Bar Chart":
        x_col = st.selectbox("Category Column", columns)
        y_col = st.selectbox("Value Column", columns)
        hue_col = st.selectbox("Color (Hue)", ["None"] + columns)
        
        if x_col == y_col:
            st.warning("Category and value columns are the same — select different columns for a meaningful bar chart.")
        else:
            # Plotly handles NaN values gracefully, so no need for dropna
            cols_needed = [x_col, y_col]
            color = hue_col if hue_col != "None" else None
            if color and color not in cols_needed:
                cols_needed.append(color)

            # Check if there's any data at all
            data_check = df[cols_needed].notna().any().any()
            if not data_check:
                st.warning(f"No data available for {', '.join(cols_needed)} - all values are null.")
            else:
                if color is None:
                    fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
                    fig.update_traces(
                        marker_color=get_color_sequence('bar'),
                        marker_line_color='rgba(255, 255, 255, 0.2)',
                        marker_line_width=1,
                        opacity=0.8
                    )
                else:
                    fig = px.bar(df, x=x_col, y=y_col, color=color, title=f"{y_col} by {x_col}")
                    fig.update_traces(marker_line_color='rgba(255, 255, 255, 0.2)', marker_line_width=1, opacity=0.8)
                fig.update_layout(height=480)
                render_plotly_with_fallback(apply_neuro_theme(fig), "Bar Chart") 

    elif chart_type == "Histogram":
        col = st.selectbox("Target Column", columns)
        bins = st.slider("Number of Bins", 5, 100, 20)
        hue_col = st.selectbox("Color (Hue)", ["None"] + columns)
        
        cols_needed = [col]
        color = hue_col if hue_col != "None" else None
        if color and color != col:
            cols_needed.append(color)

        # Check if there's any data at all
        data_check = df[cols_needed].notna().any().any()
        if not data_check:
            st.warning(f"No values available in {col} - all values are null.")
        else:
            if color is None:
                fig = px.histogram(df, x=col, nbins=bins, title=f"Distribution of {col}")
                # Explicitly set border to ensure visibility
                fig.update_traces(
                    marker_color=get_color_sequence('histogram'),
                    marker_line_color='rgba(255, 255, 255, 0.2)',
                    marker_line_width=1,
                    opacity=0.8
                )
            else:
                # Use df for histogram with color
                fig = px.histogram(df, x=col, nbins=bins, color=color, title=f"Distribution of {col}")
                fig.update_traces(marker_line_color='rgba(255, 255, 255, 0.2)', marker_line_width=1, opacity=0.8)
            fig.update_layout(height=420)
            if not render_plotly_with_fallback(apply_neuro_theme(fig), "Histogram"):
                # Try matplotlib histogram as fallback
                fig_mpl = create_matplotlib_histogram(df, col, f"Distribution of {col}")
                if fig_mpl:
                    st.pyplot(fig_mpl) 
            
    elif chart_type == "Box Plot":
        x_col = st.selectbox("Group By (X)", columns)
        y_col = st.selectbox("Value (Y)", columns)
        
        if x_col == y_col:
            st.warning("Group-by and value columns are the same — pick different columns for a valid box plot.")
        else:
            # Check if there's any data at all
            data_check = df[[x_col, y_col]].notna().any().any()
            if not data_check:
                st.warning(f"No data for Box Plot - all values are null.")
            else:
                fig = px.box(df, x=x_col, y=y_col, title=f"Box Plot of {y_col} by {x_col}")
                fig.update_traces(
                    marker_color=get_color_sequence('bar'),
                    marker_line_color='rgba(255, 255, 255, 0.2)',
                    marker_line_width=1,
                    opacity=0.8
                )
                fig.update_layout(height=480)
                if not render_plotly_with_fallback(apply_neuro_theme(fig), "Box Plot"):
                    # Try matplotlib box plot as fallback
                    fig_mpl = create_matplotlib_boxplot(df, x_col, y_col, f"Box Plot of {y_col} by {x_col}")
                    if fig_mpl:
                        st.pyplot(fig_mpl)

    elif chart_type == "Violin Plot":
        x_col = st.selectbox("Group By (X)", columns)
        y_col = st.selectbox("Value (Y)", columns)
        
        if x_col == y_col:
            st.warning("Group-by and value columns are the same — pick different columns for a valid violin plot.")
        else:
            # Check if there's any data at all
            data_check = df[[x_col, y_col]].notna().any().any()
            if not data_check:
                st.warning(f"No data for Violin Plot - all values are null.")
            else:
                fig = px.violin(df, x=x_col, y=y_col, box=True, points="all", title=f"Violin Plot of {y_col} by {x_col}")
                fig.update_traces(
                    marker_color=get_color_sequence('bar'),
                    marker_line_color='rgba(255, 255, 255, 0.2)',
                    marker_line_width=1,
                    opacity=0.8
                )
                fig.update_layout(height=480)
                render_plotly_with_fallback(apply_neuro_theme(fig), "Violin Plot")

    elif chart_type == "Line Chart":
        x_col = st.selectbox("X Axis (Time/Seq)", columns)
        y_col = st.selectbox("Y Axis (Value)", columns)
        
        if x_col == y_col:
            st.warning("X and Y axes are identical — select a different axis or use one column against the DataFrame index.")
        else:
            # Check if there's any data at all
            data_check = df[[x_col, y_col]].notna().any().any()
            if not data_check:
                st.warning(f"No data for Line Chart - all values are null.")
            else:
                fig = px.line(df, x=x_col, y=y_col, markers=True, title=f"Line Chart: {y_col} over {x_col}")
                fig.update_traces(line_color=get_color_sequence('scatter'))
                fig.update_layout(height=460)
                render_plotly_with_fallback(apply_neuro_theme(fig), "Line Chart")

    elif chart_type == "Area Chart":
        x_col = st.selectbox("X Axis (Time/Seq)", columns)
        y_col = st.selectbox("Y Axis (Value)", columns)
        
        if x_col == y_col:
            st.warning("X and Y axes are identical — select a different axis for an area chart.")
        else:
            # Check if there's any data at all
            data_check = df[[x_col, y_col]].notna().any().any()
            if not data_check:
                st.warning(f"No data for Area Chart - all values are null.")
            else:
                fig = px.area(df, x=x_col, y=y_col, title=f"Area Chart: {y_col} over {x_col}")
                fig.update_traces(line_color=get_color_sequence('scatter'))
                fig.update_layout(height=460)
                render_plotly_with_fallback(apply_neuro_theme(fig), "Area Chart")

    elif chart_type == "Pie Chart":
        cat_col = st.selectbox("Category Column", columns)
        val_col = st.selectbox("Values Column (Optional)", ["None"] + columns)
        
        # Check if there's any data at all
        cols_to_check = [cat_col]
        if val_col != "None":
            cols_to_check.append(val_col)
        data_check = df[cols_to_check].notna().any().any()
        if not data_check:
            st.warning(f"No values for pie chart - all values are null.")
        else:
            if val_col != "None":
                fig = px.pie(df, names=cat_col, values=val_col, title=f"Pie Chart of {cat_col} (weighted by {val_col})", hole=0.4, color_discrete_sequence=get_color_sequence('bar'))
            else:
                fig = px.pie(df, names=cat_col, title=f"Pie Chart of {cat_col} counts", hole=0.4, color_discrete_sequence=get_color_sequence('bar'))

            fig.update_traces(
                marker=dict(line=dict(color='rgba(255, 255, 255, 0.2)', width=1)),
                opacity=0.9
            )
            fig.update_layout(height=420)
            render_plotly_with_fallback(apply_neuro_theme(fig), "Pie Chart")

    elif chart_type == "Sunburst Chart":
        cat_cols = st.multiselect("Hierarchy Columns (Select >1)", columns)
        val_col = st.selectbox("Values Column (Optional)", ["None"] + columns)
        if st.button("Generate Plot"):
            if cat_cols:
                # Check if there's any data at all
                cols_to_check = cat_cols.copy()
                if val_col != "None":
                    cols_to_check.append(val_col)
                data_check = df[cols_to_check].notna().any().any()
                if not data_check:
                    st.warning(f"No data for sunburst chart - all values are null.")
                else:
                    values = val_col if val_col != "None" else None
                    fig = px.sunburst(df, path=cat_cols, values=values, title="Sunburst Hierarchy")
                    render_plotly_with_fallback(apply_neuro_theme(fig), "Sunburst Chart")
            else:
                st.warning("Select at least one category column.")

    elif chart_type == "Heatmap":
        st.write("Correlation Heatmap of Numerical Columns")
        
        numeric_df = df.select_dtypes(include=['float64', 'int64'])
        if numeric_df.empty:
            st.warning("No numerical columns found for correlation heatmap.")
        else:
            # Check if there's any data at all
            data_check = numeric_df.notna().any().any()
            if not data_check:
                st.warning("No numerical data available - all values are null.")
            else:
                corr = numeric_df.corr()
                fig = px.imshow(corr, text_auto='.2f', color_continuous_scale=get_color_sequence('correlation'), title='Correlation Heatmap', aspect='auto')
                fig.update_layout(height=650)
                render_plotly_with_fallback(apply_neuro_theme(fig), "Correlation Heatmap")

    # Seaborn plotting section
    else:
        if chart_type == "Pair Plot":
            st.subheader("Seaborn Pair Plot")
            st.write("Shows pairwise relationships between numeric variables")
            fig = create_seaborn_plot(df, "pairplot")
            if fig:
                st.pyplot(fig)
            else:
                st.warning("Need at least 2 numeric columns for pair plot.")

        elif chart_type == "Correlation Heatmap":
            st.subheader("Seaborn Correlation Heatmap")
            st.write("Statistical correlation matrix with seaborn styling")
            fig = create_seaborn_plot(df, "heatmap")
            if fig:
                st.pyplot(fig)
            else:
                st.warning("Need at least 2 numeric columns for correlation heatmap.")

        elif chart_type == "Box Plot":
            st.subheader("Seaborn Box Plot")
            cat_cols = [col for col in columns if df[col].dtype == 'object' or df[col].nunique() < 20]
            num_cols = [col for col in columns if df[col].dtype in ['int64', 'float64']]

            if cat_cols and num_cols:
                cat_col = st.selectbox("Category Column", cat_cols)
                num_col = st.selectbox("Numeric Column", num_cols)
                fig = create_seaborn_plot(df, "boxplot", cat_col=cat_col, num_col=num_col)
                if fig:
                    st.pyplot(fig)
                else:
                    st.warning("No valid data for box plot.")
            else:
                st.warning("Need both categorical and numeric columns for box plot.")

        elif chart_type == "Violin Plot":
            st.subheader("Seaborn Violin Plot")
            cat_cols = [col for col in columns if df[col].dtype == 'object' or df[col].nunique() < 20]
            num_cols = [col for col in columns if df[col].dtype in ['int64', 'float64']]

            if cat_cols and num_cols:
                cat_col = st.selectbox("Category Column", cat_cols)
                num_col = st.selectbox("Numeric Column", num_cols)
                fig = create_seaborn_plot(df, "violinplot", cat_col=cat_col, num_col=num_col)
                if fig:
                    st.pyplot(fig)
                else:
                    st.warning("No valid data for violin plot.")
            else:
                st.warning("Need both categorical and numeric columns for violin plot.")

        elif chart_type == "Scatter Plot":
            st.subheader("Seaborn Scatter Plot with Regression")
            num_cols = [col for col in columns if df[col].dtype in ['int64', 'float64']]

            if len(num_cols) >= 2:
                x_col = st.selectbox("X Axis", num_cols)
                y_col = st.selectbox("Y Axis", num_cols, index=1 if len(num_cols) > 1 else 0)
                hue_options = ["None"] + [col for col in columns if df[col].nunique() < 20]
                hue_col = st.selectbox("Color (Hue)", hue_options)

                fig = create_seaborn_plot(df, "scatterplot", x_col=x_col, y_col=y_col, hue_col=hue_col if hue_col != "None" else None)
                if fig:
                    st.pyplot(fig)
                else:
                    st.warning("No valid data for scatter plot.")
            else:
                st.warning("Need at least 2 numeric columns for scatter plot.")
