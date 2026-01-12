import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
import base64
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
from ui import section_header

def generate_automated_insights(df):
    """Generate automated insights from the dataset"""
    insights = {
        'dataset_overview': {},
        'data_quality': {},
        'statistical_insights': {},
        'recommendations': []
    }

    # Dataset overview
    insights['dataset_overview'] = {
        'shape': df.shape,
        'columns': len(df.columns),
        'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
        'categorical_columns': len(df.select_dtypes(include=['object', 'category']).columns),
        'missing_percentage': (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
    }

    # Data quality insights
    missing_by_col = (df.isnull().sum() / len(df)) * 100
    high_missing_cols = missing_by_col[missing_by_col > 20].index.tolist()

    insights['data_quality'] = {
        'high_missing_columns': high_missing_cols,
        'duplicate_rows': df.duplicated().sum(),
        'columns_with_outliers': []
    }

    # Statistical insights
    numeric_df = df.select_dtypes(include=[np.number])
    if not numeric_df.empty:
        insights['statistical_insights'] = {
            'correlations': numeric_df.corr().abs().max().max(),
            'skewness': numeric_df.skew().abs().mean(),
            'kurtosis': numeric_df.kurtosis().abs().mean()
        }

        # Detect potential outliers using IQR
        for col in numeric_df.columns:
            Q1 = numeric_df[col].quantile(0.25)
            Q3 = numeric_df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((numeric_df[col] < (Q1 - 1.5 * IQR)) | (numeric_df[col] > (Q3 + 1.5 * IQR))).sum()
            if outliers > len(df) * 0.05:  # More than 5% outliers
                insights['data_quality']['columns_with_outliers'].append(col)

    # Generate recommendations
    if insights['dataset_overview']['missing_percentage'] > 10:
        insights['recommendations'].append("High missing data detected. Consider imputation strategies.")

    if insights['data_quality']['duplicate_rows'] > 0:
        insights['recommendations'].append(f"Found {insights['data_quality']['duplicate_rows']} duplicate rows. Consider removing duplicates.")

    if insights['data_quality']['columns_with_outliers']:
        insights['recommendations'].append(f"Outliers detected in: {', '.join(insights['data_quality']['columns_with_outliers'])}. Consider robust scaling or removal.")

    if len(df.columns) > 50:
        insights['recommendations'].append("Large number of features detected. Consider feature selection techniques.")

    return insights

def create_executive_summary(insights):
    """Create an executive summary from insights"""
    summary = f"""
# Executive Summary - Data Analysis Report

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Dataset Overview
- **Shape:** {insights['dataset_overview']['shape'][0]} rows × {insights['dataset_overview']['shape'][1]} columns
- **Data Types:** {insights['dataset_overview']['numeric_columns']} numeric, {insights['dataset_overview']['categorical_columns']} categorical
- **Missing Data:** {insights['dataset_overview']['missing_percentage']:.1f}%

## Key Findings

### Data Quality
"""

    if insights['data_quality']['high_missing_columns']:
        summary += f"- **High missing data** in columns: {', '.join(insights['data_quality']['high_missing_columns'][:3])}\n"
    else:
        summary += "- **Good data completeness** - Low missing values across columns\n"

    if insights['data_quality']['duplicate_rows'] > 0:
        summary += f"- **{insights['data_quality']['duplicate_rows']} duplicate rows** detected\n"
    else:
        summary += "- **No duplicate rows** found\n"

    if insights['data_quality']['columns_with_outliers']:
        summary += f"- **Outliers detected** in: {', '.join(insights['data_quality']['columns_with_outliers'][:3])}\n"

    summary += "\n## Recommendations\n"
    if insights['recommendations']:
        for rec in insights['recommendations']:
            summary += f"- {rec}\n"
    else:
        summary += "- Dataset appears clean and ready for analysis\n"

    return summary

def export_to_json(df, insights, filename="analysis_report.json"):
    """Export analysis results to JSON"""
    export_data = {
        'metadata': {
            'export_date': datetime.now().isoformat(),
            'dataset_shape': df.shape,
            'columns': df.columns.tolist()
        },
        'insights': insights,
        'data_preview': df.head(10).to_dict('records')
    }

    return json.dumps(export_data, indent=2, default=str)

def export_to_csv(df, filename="dataset_export.csv"):
    """Export dataframe to CSV"""
    return df.to_csv(index=False)

def create_visualization_summary(df):
    """Create a summary of key visualizations"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=['Data Types Distribution', 'Missing Values', 'Numeric Distributions', 'Correlation Heatmap'],
        specs=[[{'type': 'pie'}, {'type': 'bar'}],
               [{'type': 'histogram'}, {'type': 'heatmap'}]]
    )

    # Data types pie chart
    dtype_counts = df.dtypes.value_counts()
    fig.add_trace(go.Pie(labels=dtype_counts.index.astype(str), values=dtype_counts.values,
                        name="Data Types"), 1, 1)

    # Missing values bar chart
    missing_pct = (df.isnull().sum() / len(df)) * 100
    missing_pct = missing_pct[missing_pct > 0]  # Only show columns with missing values
    if len(missing_pct) > 0:
        fig.add_trace(go.Bar(x=missing_pct.index, y=missing_pct.values,
                            name="Missing %"), 1, 2)
    else:
        fig.add_trace(go.Bar(x=['No Missing Data'], y=[0], name="Missing %"), 1, 2)

    # Numeric distributions
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        # Show distribution of first numeric column
        fig.add_trace(go.Histogram(x=df[numeric_cols[0]], name=f"Distribution: {numeric_cols[0]}"), 2, 1)
    else:
        fig.add_trace(go.Histogram(x=[0], name="No Numeric Data"), 2, 1)

    # Correlation heatmap
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()
        fig.add_trace(go.Heatmap(z=corr_matrix.values,
                                x=corr_matrix.columns,
                                y=corr_matrix.columns,
                                colorscale='RdBu',
                                name="Correlation"), 2, 2)
    else:
        fig.add_trace(go.Heatmap(z=[[1]], x=['Single Column'], y=['Single Column'],
                                name="Correlation"), 2, 2)

    fig.update_layout(height=800, title_text="Data Analysis Summary Dashboard")
    return fig

def show_export_reporting_suite(df):
    """Main export and reporting interface"""
    section_header("📊 Export & Reporting Suite", "Generate comprehensive reports and export data in multiple formats")

    # Generate insights
    with st.spinner("Analyzing dataset..."):
        insights = generate_automated_insights(df)

    # Executive Summary
    with st.expander("📋 Executive Summary", expanded=True):
        summary = create_executive_summary(insights)
        st.markdown(summary)

        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Dataset Size", f"{insights['dataset_overview']['shape'][0]} rows")
        with col2:
            st.metric("Features", insights['dataset_overview']['shape'][1])
        with col3:
            st.metric("Missing Data", f"{insights['dataset_overview']['missing_percentage']:.1f}%")
        with col4:
            quality_score = 100 - insights['dataset_overview']['missing_percentage']
            st.metric("Quality Score", f"{quality_score:.1f}%")

    # Visualization Summary
    with st.expander("📈 Visual Summary Dashboard"):
        fig = create_visualization_summary(df)
        st.plotly_chart(fig, use_container_width=True)

    # Export Options
    st.markdown("---")
    with st.expander("💾 Export Options", expanded=True):
        tab1, tab2, tab3, tab4 = st.tabs(["📄 PDF Report", "📊 JSON Export", "📋 CSV Export", "🔗 API Endpoint"])

        with tab1:
            st.markdown("### Generate PDF Report")
            report_title = st.text_input("Report Title", "Neurolytix AI Analysis Report")
            include_visualizations = st.checkbox("Include Visualizations", value=True)

            if st.button("Generate PDF Report"):
                with st.spinner("Generating PDF report..."):
                    # Create PDF with enhanced content
                    pdf = PDF()
                    pdf.add_page()

                    # Title
                    pdf.set_font('Arial', 'B', 16)
                    pdf.cell(0, 10, report_title, 0, 1, 'C')
                    pdf.ln(10)

                    # Executive Summary
                    pdf.chapter_title("Executive Summary")
                    summary_text = create_executive_summary(insights)
                    # Clean markdown for PDF
                    summary_text = summary_text.replace('#', '').replace('*', '').replace('-', '•')
                    pdf.chapter_body(summary_text)

                    # Dataset Overview
                    pdf.chapter_title("Dataset Overview")
                    overview_text = f"""
Dataset Shape: {insights['dataset_overview']['shape'][0]} rows × {insights['dataset_overview']['shape'][1]} columns
Numeric Columns: {insights['dataset_overview']['numeric_columns']}
Categorical Columns: {insights['dataset_overview']['categorical_columns']}
Missing Data: {insights['dataset_overview']['missing_percentage']:.1f}%
"""
                    pdf.chapter_body(overview_text)

                    # Recommendations
                    if insights['recommendations']:
                        pdf.chapter_title("Recommendations")
                        rec_text = "\n".join(f"• {rec}" for rec in insights['recommendations'])
                        pdf.chapter_body(rec_text)

                    # Convert to bytes for download
                    pdf_bytes = pdf.output(dest='S').encode('latin-1')

                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"{report_title.replace(' ', '_')}.pdf",
                        mime="application/pdf"
                    )

        with tab2:
            st.markdown("### Export as JSON")
            include_data_preview = st.checkbox("Include Data Preview", value=True)

            if st.button("Generate JSON Export"):
                json_data = export_to_json(df, insights)

                st.download_button(
                    label="📥 Download JSON Report",
                    data=json_data,
                    file_name="analysis_report.json",
                    mime="application/json"
                )

                # Show preview
                st.json(json.loads(json_data))

        with tab3:
            st.markdown("### Export Dataset as CSV")
            include_index = st.checkbox("Include Index Column", value=False)

            if st.button("Generate CSV Export"):
                csv_data = df.to_csv(index=include_index)

                st.download_button(
                    label="📥 Download CSV Dataset",
                    data=csv_data,
                    file_name="dataset_export.csv",
                    mime="text/csv"
                )

                st.success(f"Ready to export {len(df)} rows × {len(df.columns)} columns")

        with tab4:
            st.markdown("### API Endpoint Information")
            st.info("🚧 API endpoints will be implemented in the next update.")

            st.code("""
# Planned API Endpoints:
GET  /api/v1/datasets/{id}/insights    # Get automated insights
POST /api/v1/datasets/{id}/export      # Export in various formats
GET  /api/v1/models/{id}/predictions  # Get model predictions
POST /api/v1/reports/generate         # Generate automated reports
""", language="python")

            st.markdown("**Current Status:** Local API server can be started with:")
            st.code("python -m uvicorn api:app --reload", language="bash")

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Neurolytix AI - Analysis Report', 0, 1, 'C')
        self.ln(5)
        self.set_draw_color(0, 210, 255) # Cyan
        self.set_line_width(0.5)
        self.line(10, 25, 200, 25)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.set_text_color(50)
        self.multi_cell(0, 7, str(body))
        self.ln()

    def add_plot_image(self, image_path, w=100):
        if hasattr(self, 'get_y'):
             y = self.get_y()
        else:
             y = 0
        # Check if we have space, else add page
        if y > 220: 
            self.add_page()
            
        try:
            self.image(image_path, w=w, x=(210-w)/2)
            self.ln(5)
        except Exception as e:
            self.chapter_body(f"[Error embedding image: {e}]")

def create_download_link(val, filename):
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}" style="padding:10px; background:#00d2ff; color:white; text-decoration:none; border-radius:5px; font-weight:bold;">Download PDF Report</a>'

def show_reporting(df):
    section_header("Automated Reporting", "Generate a comprehensive summary of your analysis.")
    
    st.write("Generate a PDF report containing dataset statistics and insights.")
    
    # Optional: User Notes
    notes = st.text_area("Add Custom Notes/Executive Summary", "Enter any specific observations here...")
    
    if st.button("Generate Report"):
        with st.spinner("Generating PDF Report..."):
            pdf = PDF()
            pdf.add_page()
            
            # 1. Executive Summary
            pdf.chapter_title("1. Executive Summary")
            pdf.chapter_body(notes)
            pdf.ln(5)
            
            # 2. Dataset Info
            pdf.chapter_title("2. Dataset Overview")
            info_text = f"Total Rows: {df.shape[0]}\nTotal Columns: {df.shape[1]}\nMissing Values: {df.isnull().sum().sum()}\nDuplicate Rows: {df.duplicated().sum()}"
            pdf.chapter_body(info_text)
            
            # 3. Numerical Statistics
            pdf.chapter_title("3. Numerical Statistics (Top Features)")
            # Get numeric cols
            nums = df.select_dtypes(include=['number'])
            if not nums.empty:
                # Limit to top 8 columns to fit in PDF width nicely or summarize
                desc = nums.describe().T.reset_index().rename(columns={'index': 'Feature'})
                desc = desc[['Feature', 'mean', 'std', 'min', 'max']].head(15) # Top 15 features
                
                # Simple table layout
                pdf.set_font('Courier', '', 8)
                # Header
                header = f"{'Feature':<25} {'Mean':<15} {'Std':<15} {'Min':<15} {'Max':<15}"
                pdf.cell(0, 5, header, 0, 1)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                
                for index, row in desc.iterrows():
                    f_name = str(row['Feature'])[:24]
                    txt = f"{f_name:<25} {row['mean']:<15.2f} {row['std']:<15.2f} {row['min']:<15.2f} {row['max']:<15.2f}"
                    pdf.cell(0, 5, txt, 0, 1)
                
                pdf.ln(5)
            else:
                pdf.chapter_body("No numeric columns found.")
            
            # 4. Categorical Overview
            pdf.chapter_title("4. Categorical Overview")
            cats = df.select_dtypes(include=['object', 'category'])
            if not cats.empty:
                pdf.set_font('Courier', '', 8)
                for col in cats.columns[:10]: # Limit to 10
                    top = df[col].value_counts().head(3).to_dict()
                    top_str = ", ".join([f"{k} ({v})" for k,v in top.items()])
                    pdf.multi_cell(0, 5, f"{col}: {top_str}")
            else:
                 pdf.chapter_body("No categorical columns found.")

            # Output
            try:
                pdf_bytes = pdf.output(dest='S').encode('latin-1')
            except Exception as e:
                # FPDF2 might return bytearray directly in output() if no dest given, or might fail
                # Trying standard bytes output
                try:
                    pdf_bytes = pdf.output()
                except Exception:
                     st.error(f"PDF generation failed: {e}")
                     return

            html = create_download_link(pdf_bytes, "Neurolytix_Report.pdf")
            st.markdown(html, unsafe_allow_html=True)
            st.success("Report Generated Successfully!")
