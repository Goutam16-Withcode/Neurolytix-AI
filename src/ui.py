import streamlit as st
import pandas as pd

def load_custom_css(module_name="Global"):
    # Define route-specific color palettes
    palettes = {
        "Data Overview": {"primary": "#00d2ff", "rgb": "0, 210, 255", "glow": "rgba(0, 210, 255, 0.4)"},
        "Visual Analytics": {"primary": "#ff00cc", "rgb": "255, 0, 204", "glow": "rgba(255, 0, 204, 0.4)"},
        "Statistical Analysis": {"primary": "#ffcc00", "rgb": "255, 204, 0", "glow": "rgba(255, 204, 0, 0.4)"},
        "Smart Cleaning": {"primary": "#00ff88", "rgb": "0, 255, 136", "glow": "rgba(0, 255, 136, 0.4)"},
        "Auto Feature Engineering": {"primary": "#ff8800", "rgb": "255, 136, 0", "glow": "rgba(255, 136, 0, 0.4)"},
        "AutoML (Supervised)": {"primary": "#7000ff", "rgb": "112, 0, 255", "glow": "rgba(112, 0, 255, 0.4)"},
        "Unsupervised Learning": {"primary": "#00ffff", "rgb": "0, 255, 255", "glow": "rgba(0, 255, 255, 0.4)"},
        "Fairness Checking": {"primary": "#ffffff", "rgb": "255, 255, 255", "glow": "rgba(255, 255, 255, 0.4)"},
        "Model Deployment": {"primary": "#ff3333", "rgb": "255, 51, 51", "glow": "rgba(255, 51, 51, 0.4)"},
        "Data Drift Monitoring": {"primary": "#33ff33", "rgb": "51, 255, 51", "glow": "rgba(51, 255, 51, 0.4)"},
        "Multi-Modal Analysis": {"primary": "#cc00ff", "rgb": "204, 0, 255", "glow": "rgba(204, 0, 255, 0.4)"},
        "Collaborative Analysis": {"primary": "#0066ff", "rgb": "0, 102, 255", "glow": "rgba(0, 102, 255, 0.4)"},
        "Auto Hypothesis Gen": {"primary": "#ff99ff", "rgb": "255, 153, 255", "glow": "rgba(255, 153, 255, 0.4)"},
        "Multi-Agent AI Team": {"primary": "#00ffcc", "rgb": "0, 255, 204", "glow": "rgba(0, 255, 204, 0.4)"},
        "AI Insights (Narrative)": {"primary": "#ffff00", "rgb": "255, 255, 0", "glow": "rgba(255, 255, 0, 0.4)"},
        "Business Recs": {"primary": "#00ff00", "rgb": "0, 255, 0", "glow": "rgba(0, 255, 0, 0.4)"},
        "Autonomous Data Scientist": {"primary": "#ff0000", "rgb": "255, 0, 0", "glow": "rgba(255, 0, 0, 0.4)"},
        "AI Assistant": {"primary": "#8888ff", "rgb": "136, 136, 255", "glow": "rgba(136, 136, 255, 0.4)"},
        "AI Data Agent": {"primary": "#8888ff", "rgb": "136, 136, 255", "glow": "rgba(136, 136, 255, 0.4)"},
        "Reporting": {"primary": "#ffaaaa", "rgb": "255, 170, 170", "glow": "rgba(255, 170, 170, 0.4)"},
        "Default": {"primary": "#00d2ff", "rgb": "0, 210, 255", "glow": "rgba(0, 210, 255, 0.3)"}
    }
    
    theme = palettes.get(module_name, palettes["Default"])
    primary = theme["primary"]
    primary_rgb = theme["rgb"]
    glow = theme["glow"]

    css = f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@300;500;700&display=swap');

        :root {{
            --primary: {primary};
            --primary-rgb: {primary_rgb};
            --accent-glow: {glow};
            --bg-dark: #050510;
            --glass-bg: rgba(10, 10, 25, 0.85);
            --glass-border: rgba(255, 255, 255, 0.1);
        }}

        /* Futuristic Background with Parallax Neural Pulse */
        .stApp {{
            background-color: var(--bg-dark);
            background-image: 
                radial-gradient(circle at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba({primary_rgb}, 0.15) 0%, transparent 50%),
                linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 100% 100%, 40px 40px, 40px 40px;
            color: #ffffff !important;
            font-family: 'Outfit', sans-serif;
            animation: neuralFloat 20s ease-in-out infinite;
        }}

        @keyframes neuralFloat {{
            0%, 100% {{ background-position: 0% 0%; }}
            50% {{ background-position: 5% 5%; }}
        }}

        /* 3D NEON CARD SYSTEM */
        .neuro-card, div[data-testid="stMetric"], .stDataFrame, .stExpander {{
            background: var(--glass-bg) !important;
            backdrop-filter: blur(25px) !important;
            -webkit-backdrop-filter: blur(25px) !important;
            border-radius: 20px !important;
            border: 1px solid var(--glass-border) !important;
            padding: 24px !important;
            box-shadow: 0 10px 40px rgba(0,0,0,0.8) !important;
            margin-bottom: 30px !important;
            transition: all 0.5s cubic-bezier(0.23, 1, 0.32, 1);
            position: relative;
            transform-style: preserve-3d;
            perspective: 1000px;
        }}

        /* Moving Border Light Effect */
        .neuro-card::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            border-radius: 20px;
            padding: 2px;
            background: linear-gradient(90deg, transparent, var(--primary), transparent);
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            opacity: 0;
            transition: 0.5s;
            animation: borderRotate 4s linear infinite;
        }}

        @keyframes borderRotate {{
            0% {{ background-position: 0% 50%; }}
            100% {{ background-position: 200% 50%; }}
        }}

        .neuro-card:hover {{
            transform: translateY(-8px) rotateX(2deg) rotateY(2deg);
            border-color: rgba({primary_rgb}, 0.5) !important;
            box-shadow: 0 20px 60px rgba({primary_rgb}, 0.3) !important;
        }}
        
        .neuro-card:hover::before {{
            opacity: 1;
        }}

        /* PLOTLY CHART STYLING - Glassmorphism */
        div[data-testid="stPlotlyChart"] {{
            background: rgba(15, 15, 35, 0.4) !important;
            backdrop-filter: blur(15px) !important;
            border-radius: 20px !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            padding: 15px !important;
            margin-bottom: 35px !important;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5) !important;
        }}

        /* Ultra-Modern Text Styling */
        h1, h2, h3 {{
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: -1px;
            background: linear-gradient(135deg, #fff 0%, var(--primary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 10px 20px rgba(0,0,0,0.5);
        }}

        /* Interactive Sidebar */
        section[data-testid="stSidebar"] {{
            background: rgba(2, 2, 8, 0.98) !important;
            border-right: 1px solid rgba({primary_rgb}, 0.2);
            box-shadow: 5px 0 30px rgba(0,0,0,0.5);
        }}

        /* GLOBAL NEON HEADER */
        .neuro-header {{
            background: rgba(10, 10, 25, 0.4) !important;
            backdrop-filter: blur(15px) !important;
            border-bottom: 1px solid rgba({primary_rgb}, 0.2);
            padding: 20px 40px !important;
            margin: -60px -100px 40px -100px !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-size: 2.2rem !important;
            font-weight: 800 !important;
            letter-spacing: 8px !important;
            text-align: center;
            color: #fff;
            text-shadow: 0 0 20px rgba({primary_rgb}, 0.3);
            position: sticky;
            top: 0;
            z-index: 999;
        }}

        /* Sidebar Adjustments */
        [data-testid="stSidebarNav"]::before {{
            content: "NAVIGATION HUB";
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 600;
            font-size: 0.8rem;
            letter-spacing: 3px;
            color: #555;
            display: block;
            text-align: center;
            padding: 20px 10px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            margin-bottom: 20px;
        }}

        /* Sidebar Item - Holographic Style */
        [data-testid="stSidebar"] div[data-testid="stRadio"] > label {{
            background: rgba(255,255,255,0.03) !important;
            border: 1px solid rgba(255,255,255,0.05) !important;
            margin-bottom: 10px !important;
            border-radius: 12px !important;
            padding: 15px 20px !important;
            transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            color: #888 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.9rem;
        }}

        [data-testid="stSidebar"] div[data-testid="stRadio"] > label:hover {{
            background: rgba({primary_rgb}, 0.15) !important;
            border-color: var(--primary) !important;
            color: #fff !important;
            transform: scale(1.05) translateX(12px);
            box-shadow: -15px 0 30px rgba({primary_rgb}, 0.3);
        }}

        [data-testid="stSidebar"] div[data-testid="stRadio"] [aria-checked="true"] + div {{
            color: var(--primary) !important;
            font-weight: 900 !important;
            text-shadow: 0 0 15px var(--accent-glow);
            letter-spacing: 2px;
        }}

        [data-testid="stSidebar"] div[data-testid="stRadio"] [aria-checked="true"] {{
            border-color: var(--primary) !important;
            border-width: 2px !important;
        }}

        /* Neon Metrics Pulse */
        [data-testid="stMetricValue"] {{
            color: var(--primary) !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-size: 2.5rem !important;
            animation: textPulse 2s ease-in-out infinite;
        }}

        @keyframes textPulse {{
            0%, 100% {{ text-shadow: 0 0 10px var(--accent-glow); }}
            50% {{ text-shadow: 0 0 25px var(--accent-glow), 0 0 40px var(--primary); }}
        }}

        /* Ensure sub-elements don't block interaction */
        iframe {{
            border-radius: 20px !important;
        }}

        /* Remove Default Streams */
        header, footer, #MainMenu {{ visibility: hidden !important; }}
        section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
            display: none;
        }}

        </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def section_header(title, subtitle=None):
    st.markdown(f"""
        <div style="margin-bottom: 40px; border-left: 5px solid var(--primary); padding: 5px 25px;">
            <h1 style="margin:0; font-size: 3rem; letter-spacing: -2px; text-transform: uppercase;">{title}</h1>
            {f'<p style="margin:5px 0 0 0; opacity:0.6; font-size: 1.1rem; font-weight: 300; letter-spacing: 1px;">{subtitle}</p>' if subtitle else ''}
        </div>
    """, unsafe_allow_html=True)

def display_card(content):
    st.markdown(f"""
        <div class="stCard">
            {content}
        </div>
    """, unsafe_allow_html=True)

def apply_neuro_theme(fig):
    """
    Centralized Plotly theme application for Neurolytix AI.
    Forced Dark Mode with Cyan highlights to match overall app aesthetic.
    Uses 'plotly_dark' to avoid white background conflicts.

    Important: this function no longer overrides per-trace colors so that
    individual plotting helpers can choose color palettes per chart type.
    """
    # 1. Base Layout (apply defaults but do not force trace colors)
    layout_updates = dict(
        template="plotly_dark",
        plot_bgcolor='rgba(20,20,35,0.9)',
        paper_bgcolor='rgba(20,20,35,0.9)',
        font=dict(color="#e0e0e0", family="Outfit", size=12),
        margin=dict(l=60, r=40, t=60, b=40),
        hovermode='closest',
        showlegend=True,
        title_font_size=18,
        title_font_color="#00d2ff",
        legend=dict(
            bgcolor='rgba(20,20,35,0.8)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1,
            font=dict(color='#e0e0e0', size=10)
        )
    )
    # Set a reasonable default height if the caller didn't set one
    if getattr(fig.layout, 'height', None) is None:
        layout_updates['height'] = 450
    fig.update_layout(**layout_updates)

    # Dark theme axis styling
    fig.update_xaxes(
        gridcolor='rgba(255,255,255,0.1)',
        tickfont=dict(color='rgba(255,255,255,0.8)', size=11),
        linecolor='rgba(255,255,255,0.2)',
        autorange=True,
        showgrid=True,
        zeroline=False
    )
    fig.update_yaxes(
        gridcolor='rgba(255,255,255,0.1)',
        tickfont=dict(color='rgba(255,255,255,0.8)', size=11),
        linecolor='rgba(255,255,255,0.2)',
        autorange=True,
        showgrid=True,
        zeroline=False
    )

    # Refined Scatter styling (defaults only — do not overwrite colors if set)
    fig.update_traces(
        marker=dict(size=10, opacity=0.8, line=dict(width=1, color='#0088aa')),
        selector=dict(type=['scatter', 'scatter3d'])
    )

    # Ensure traces have a visible color if none was specified, but do not override
    for trace in fig.data:
        try:
            # Check marker.color safely
            if hasattr(trace, 'marker') and trace.marker is not None:
                # Some trace types (like Histogram) have marker but might not support color the same way, or it might be a dict
                current_color = getattr(trace.marker, 'color', None)
                if current_color is None:
                     # Only apply default if it's missing; handle dict vs object
                     if isinstance(trace.marker, dict):
                         trace.marker['color'] = '#00d2ff'
                     else:
                         try:
                             trace.marker.color = '#00d2ff'
                         except Exception:
                             pass
        except Exception:
            pass
            
        try:
            # Check line.color safely
            if hasattr(trace, 'line') and trace.line is not None:
                current_line_color = getattr(trace.line, 'color', None)
                if current_line_color is None:
                    if isinstance(trace.line, dict):
                        trace.line['color'] = '#00d2ff'
                    else:
                        try:
                            trace.line.color = '#00d2ff'
                        except Exception:
                            pass
        except Exception:
            pass

    return fig

def clean_and_validate_data(df, aggressive=False):
    import pandas as pd  # local import to ensure availability during runtime/reloads
    """
    Robust data cleaning to ensure numeric columns are actually numeric.
    Centralized utility for EDA and Visualization modules.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    aggressive : bool
        If True, attempt aggressive coercion of strings to numeric by stripping
        common formatting (commas, currency symbols, percent signs, parentheses).
    """
    df_clean = df.copy()
    coercion_report = {"coerced": [], "failed": []}

    # 1. Convert object columns to numeric if possible (first-pass)
    for col in df_clean.columns:
        if df_clean[col].dtype == 'object':
            try:
                converted = pd.to_numeric(df_clean[col], errors='coerce')
                if converted.notna().mean() > 0.5:
                    df_clean[col] = converted
                    coercion_report["coerced"].append(col)
                else:
                    coercion_report["failed"].append(col)
            except Exception:
                coercion_report["failed"].append(col)

    # 2. Aggressive coercion (strip commas, currency signs, parentheses, percent)
    if aggressive:
        for col in list(df_clean.columns):
            if df_clean[col].dtype == 'object' or col in coercion_report.get('failed', []):
                s = df_clean[col].astype(str).str.strip()
                # Convert (123) style negatives to -123
                s = s.str.replace(r"^\((.*)\)$", r"-\1", regex=True)
                # Remove currency symbols and spaces and thousands separators
                s = s.str.replace(r"[,\$£€\s]", "", regex=True)
                # Keep percent sign for later handling
                is_pct = s.str.contains('%')
                s = s.str.replace('%', '', regex=False)
                # Remove any characters that are not digits, dot, minus, or exponent
                s = s.str.replace(r"[^0-9\.\-eE]", '', regex=True)

                converted = pd.to_numeric(s, errors='coerce')
                if is_pct.any():
                    try:
                        converted.loc[is_pct] = converted.loc[is_pct] / 100.0
                    except Exception:
                        # If indexing issues occur, ignore percent conversion
                        pass

                if converted.notna().sum() > 0:
                    # Only accept the coercion if it yields at least some non-null values
                    df_clean[col] = converted
                    coercion_report.setdefault("aggressively_coerced", []).append(col)

                    # Store a small before/after preview sample for UI feedback
                    try:
                        before_sample = df[col].astype(str).head(5).tolist()
                    except Exception:
                        before_sample = []
                    try:
                        after_sample = converted.head(5).astype(object).tolist()
                    except Exception:
                        after_sample = []
                    coercion_report.setdefault('preview', {})[col] = {"before": before_sample, "after": after_sample}
                else:
                    coercion_report.setdefault("aggressive_failed", []).append(col)

    # Persist a brief report so the UI can inform users (stored in session for access)
    # Also optionally compute diagnostics for each column (helpful for EDA decisions)
    diagnostics = {}
    for col in df_clean.columns:
        diag = {}
        try:
            series = pd.to_numeric(df_clean[col], errors='coerce')
            diag['non_null'] = int(series.notna().sum())
            diag['non_null_pct'] = float(series.notna().mean())
            diag['unique'] = int(series.nunique(dropna=True))
            diag['is_constant'] = bool(series.nunique(dropna=True) <= 1)
            if series.notna().sum() > 0:
                diag['min'] = float(series.min())
                diag['max'] = float(series.max())
                diag['std'] = float(series.std())
            else:
                diag['min'] = None
                diag['max'] = None
                diag['std'] = None
        except Exception:
            diag = {'non_null': 0, 'non_null_pct': 0.0, 'unique': 0, 'is_constant': True, 'min': None, 'max': None, 'std': None}
        diagnostics[col] = diag

    try:
        import streamlit as st
        st.session_state['_coercion_report'] = coercion_report
        st.session_state['_coercion_diagnostics'] = diagnostics
    except Exception:
        pass

    return df_clean


def coerce_single_column(df, col):
    import pandas as pd  # local import to ensure availability during runtime/reloads
    """Attempt aggressive coercion for a single column. Updates session_state reports/diagnostics if successful.

    Returns True if coercion changed any values, False otherwise.
    """
    try:
        s = df[col].astype(str).str.strip()
    except Exception:
        return False

    s = s.str.replace(r"^\((.*)\)$", r"-\1", regex=True)
    s = s.str.replace(r"[,\$£€\s]", "", regex=True)
    is_pct = s.str.contains('%')
    s = s.str.replace('%', '', regex=False)
    s = s.str.replace(r"[^0-9\.\-eE]", '', regex=True)

    converted = pd.to_numeric(s, errors='coerce')
    if is_pct.any():
        try:
            converted.loc[is_pct] = converted.loc[is_pct] / 100.0
        except Exception:
            pass

    if converted.notna().sum() > 0:
        df2 = df.copy()
        df2[col] = converted

        # Update coercion report preview
        try:
            import streamlit as st
            report = st.session_state.get('_coercion_report', {})
            report.setdefault('preview', {})[col] = {
                'before': df[col].astype(str).head(5).tolist(),
                'after': converted.head(5).astype(object).tolist()
            }
            report.setdefault('aggressively_coerced', []).append(col)
            if 'aggressive_failed' in report and col in report['aggressive_failed']:
                report['aggressive_failed'].remove(col)
            st.session_state['_coercion_report'] = report

            # Update diagnostics
            diag = st.session_state.get('_coercion_diagnostics', {})
            series = pd.to_numeric(df2[col], errors='coerce')
            diag[col] = {
                'non_null': int(series.notna().sum()),
                'non_null_pct': float(series.notna().mean()),
                'unique': int(series.nunique(dropna=True)),
                'is_constant': bool(series.nunique(dropna=True) <= 1),
                'min': float(series.min()) if series.notna().sum() > 0 else None,
                'max': float(series.max()) if series.notna().sum() > 0 else None,
                'std': float(series.std()) if series.notna().sum() > 0 else None
            }
            st.session_state['_coercion_diagnostics'] = diag
        except Exception:
            pass

        return df2

    return False


def check_optional_packages(package_module_names):
    """Check if modules are importable. Returns dict with 'missing' and 'present' lists."""
    missing = []
    present = []
    try:
        import importlib
        for mod in package_module_names:
            try:
                if importlib.util.find_spec(mod) is None:
                    missing.append(mod)
                else:
                    present.append(mod)
            except Exception:
                missing.append(mod)
    except Exception:
        # Fallback: attempt import directly
        for mod in package_module_names:
            try:
                __import__(mod)
                present.append(mod)
            except Exception:
                missing.append(mod)
    return {'missing': missing, 'present': present}


def generate_requirements_snippet(packages, include_versions=False):
    """Return a requirements.txt formatted string for the given pip package names.
    If include_versions is True we could attempt to capture installed versions (best-effort).
    """
    lines = []
    for pkg in packages:
        # Return the package names as provided (no AutoViz-specific mappings)
        lines.append(pkg)
    return '\n'.join(lines) + '\n'
