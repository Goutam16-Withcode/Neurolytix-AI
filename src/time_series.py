import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from prophet import Prophet
import warnings
warnings.filterwarnings('ignore')
from ui import section_header

def detect_time_series_columns(df):
    """Detect potential time series columns"""
    ts_candidates = []

    for col in df.columns:
        if df[col].dtype in ['datetime64[ns]', 'object']:
            try:
                # Try to convert to datetime
                pd.to_datetime(df[col].dropna().head(10), errors='coerce')
                ts_candidates.append(col)
            except:
                continue

    return ts_candidates

def prepare_time_series_data(df, date_col, value_col):
    """Prepare data for time series analysis"""
    try:
        # Convert date column
        ts_df = df.copy()
        ts_df[date_col] = pd.to_datetime(ts_df[date_col], errors='coerce')

        # Drop rows with invalid dates
        ts_df = ts_df.dropna(subset=[date_col])

        # Sort by date
        ts_df = ts_df.sort_values(date_col)

        # Set date as index
        ts_df = ts_df.set_index(date_col)

        # Handle missing values in value column
        if ts_df[value_col].isnull().any():
            ts_df[value_col] = ts_df[value_col].fillna(method='ffill').fillna(method='bfill')

        return ts_df[[value_col]], "Data prepared successfully"

    except Exception as e:
        return None, f"Failed to prepare data: {str(e)}"

def perform_seasonal_decomposition(ts_data, model='additive', period=None):
    """Perform seasonal decomposition"""
    try:
        if period is None:
            # Auto-detect period based on data frequency
            freq = pd.infer_freq(ts_data.index)
            if freq:
                if 'D' in freq:
                    period = 7  # Weekly seasonality for daily data
                elif 'H' in freq:
                    period = 24  # Daily seasonality for hourly data
                elif 'M' in freq:
                    period = 12  # Yearly seasonality for monthly data
                else:
                    period = 7  # Default
            else:
                period = min(7, len(ts_data) // 2)

        decomposition = seasonal_decompose(ts_data, model=model, period=period)

        return {
            'trend': decomposition.trend,
            'seasonal': decomposition.seasonal,
            'residual': decomposition.resid,
            'observed': decomposition.observed,
            'period': period
        }, "Decomposition completed"

    except Exception as e:
        return None, f"Decomposition failed: {str(e)}"

def test_stationarity(ts_data):
    """Test for stationarity using Augmented Dickey-Fuller test"""
    try:
        result = adfuller(ts_data.dropna())

        return {
            'adf_statistic': result[0],
            'p_value': result[1],
            'critical_values': result[4],
            'is_stationary': result[1] < 0.05
        }, "Stationarity test completed"

    except Exception as e:
        return None, f"Stationarity test failed: {str(e)}"

def forecast_with_prophet(ts_data, periods=30):
    """Forecast using Facebook Prophet"""
    try:
        # Prepare data for Prophet
        prophet_df = pd.DataFrame({
            'ds': ts_data.index,
            'y': ts_data.values.flatten()
        })

        # Fit Prophet model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode='multiplicative'
        )

        model.fit(prophet_df)

        # Make future dataframe
        future = model.make_future_dataframe(periods=periods)

        # Forecast
        forecast = model.predict(future)

        return {
            'model': model,
            'forecast': forecast,
            'future': future
        }, "Prophet forecasting completed"

    except Exception as e:
        return None, f"Prophet forecasting failed: {str(e)}"

def forecast_with_arima(ts_data, order=(1,1,1), periods=30):
    """Forecast using ARIMA"""
    try:
        # Fit ARIMA model
        model = ARIMA(ts_data, order=order)
        model_fit = model.fit()

        # Forecast
        forecast = model_fit.forecast(steps=periods)

        # Create forecast index
        last_date = ts_data.index[-1]
        freq = pd.infer_freq(ts_data.index)
        if freq:
            forecast_index = pd.date_range(start=last_date, periods=periods+1, freq=freq)[1:]
        else:
            forecast_index = pd.date_range(start=last_date, periods=periods, freq='D')

        return {
            'model': model_fit,
            'forecast': forecast,
            'forecast_index': forecast_index
        }, "ARIMA forecasting completed"

    except Exception as e:
        return None, f"ARIMA forecasting failed: {str(e)}"

def show_time_series_analysis(df):
    """Main time series analysis interface"""
    section_header("📈 Interactive Time Series Analysis", "Seasonal decomposition, forecasting, and anomaly detection")

    # Detect time series columns
    ts_candidates = detect_time_series_columns(df)

    if not ts_candidates:
        st.warning("No datetime columns detected. Please ensure your data has date/time columns.")
        return

    col1, col2 = st.columns(2)

    with col1:
        date_col = st.selectbox("Select Date/Time Column", ts_candidates)

    with col2:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            st.error("No numeric columns found for time series analysis.")
            return

        value_col = st.selectbox("Select Value Column", numeric_cols)

    if st.button("Prepare Time Series Data"):
        with st.spinner("Preparing time series data..."):
            ts_data, message = prepare_time_series_data(df, date_col, value_col)

            if ts_data is not None:
                st.success(message)
                st.session_state.ts_data = ts_data
                st.session_state.ts_date_col = date_col
                st.session_state.ts_value_col = value_col

                # Show basic statistics
                st.subheader("📊 Time Series Overview")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Data Points", len(ts_data))
                with col2:
                    st.metric("Date Range", f"{ts_data.index.min().date()} to {ts_data.index.max().date()}")
                with col3:
                    st.metric("Missing Values", ts_data.isnull().sum().sum())
                with col4:
                    st.metric("Frequency", pd.infer_freq(ts_data.index) or "Irregular")

                # Basic time series plot
                fig = px.line(ts_data, x=ts_data.index, y=value_col,
                            title=f"Time Series: {value_col}")
                st.plotly_chart(fig, use_container_width=True)

            else:
                st.error(message)

    # Analysis tabs
    if 'ts_data' in st.session_state:
        st.markdown("---")
        tab1, tab2, tab3, tab4 = st.tabs(["🔍 Decomposition", "📈 Stationarity", "🔮 Forecasting", "🚨 Anomalies"])

        with tab1:
            st.subheader("Seasonal Decomposition")

            col1, col2 = st.columns(2)
            with col1:
                model_type = st.selectbox("Decomposition Model", ["additive", "multiplicative"], key="decomp_model")
            with col2:
                period = st.number_input("Period", min_value=2, max_value=min(365, len(st.session_state.ts_data)//2),
                                       value=7, key="decomp_period")

            if st.button("Perform Decomposition", key="decompose_btn"):
                with st.spinner("Performing seasonal decomposition..."):
                    decomposition, message = perform_seasonal_decomposition(
                        st.session_state.ts_data, model=model_type, period=period
                    )

                    if decomposition:
                        st.success(message)

                        # Create subplots
                        fig = make_subplots(
                            rows=4, cols=1,
                            subplot_titles=['Observed', 'Trend', 'Seasonal', 'Residual'],
                            shared_xaxes=True
                        )

                        fig.add_trace(go.Scatter(x=decomposition['observed'].index,
                                               y=decomposition['observed'].values.flatten(),
                                               name='Observed'), row=1, col=1)

                        fig.add_trace(go.Scatter(x=decomposition['trend'].index,
                                               y=decomposition['trend'].values.flatten(),
                                               name='Trend'), row=2, col=1)

                        fig.add_trace(go.Scatter(x=decomposition['seasonal'].index,
                                               y=decomposition['seasonal'].values.flatten(),
                                               name='Seasonal'), row=3, col=1)

                        fig.add_trace(go.Scatter(x=decomposition['residual'].index,
                                               y=decomposition['residual'].values.flatten(),
                                               name='Residual'), row=4, col=1)

                        fig.update_layout(height=800, title_text="Seasonal Decomposition")
                        st.plotly_chart(fig, use_container_width=True)

                    else:
                        st.error(message)

        with tab2:
            st.subheader("Stationarity Analysis")

            if st.button("Test Stationarity", key="stationarity_btn"):
                with st.spinner("Testing for stationarity..."):
                    stationarity_result, message = test_stationarity(st.session_state.ts_data.values.flatten())

                    if stationarity_result:
                        st.success(message)

                        col1, col2 = st.columns(2)

                        with col1:
                            st.metric("ADF Statistic", f"{stationarity_result['adf_statistic']:.4f}")
                            st.metric("p-value", f"{stationarity_result['p_value']:.4f}")

                        with col2:
                            status = "✅ Stationary" if stationarity_result['is_stationary'] else "❌ Non-stationary"
                            st.metric("Stationarity Test", status)

                            st.write("**Critical Values:**")
                            for key, value in stationarity_result['critical_values'].items():
                                st.write(f"{key}: {value:.4f}")

                        if not stationarity_result['is_stationary']:
                            st.info("💡 The series is non-stationary. Consider differencing or transformation.")

                    else:
                        st.error(message)

        with tab3:
            st.subheader("Time Series Forecasting")

            forecast_method = st.radio("Forecasting Method", ["Prophet", "ARIMA"], key="forecast_method")
            forecast_periods = st.slider("Forecast Periods", 7, 365, 30, key="forecast_periods")

            if forecast_method == "ARIMA":
                col1, col2, col3 = st.columns(3)
                with col1:
                    p = st.number_input("AR (p)", 0, 5, 1, key="arima_p")
                with col2:
                    d = st.number_input("I (d)", 0, 2, 1, key="arima_d")
                with col3:
                    q = st.number_input("MA (q)", 0, 5, 1, key="arima_q")

            if st.button("Generate Forecast", key="forecast_btn"):
                with st.spinner(f"Generating {forecast_method} forecast..."):
                    if forecast_method == "Prophet":
                        forecast_result, message = forecast_with_prophet(
                            st.session_state.ts_data, periods=forecast_periods
                        )
                    else:
                        order = (p, d, q)
                        forecast_result, message = forecast_with_arima(
                            st.session_state.ts_data, order=order, periods=forecast_periods
                        )

                    if forecast_result:
                        st.success(message)

                        if forecast_method == "Prophet":
                            # Plot Prophet forecast
                            fig = go.Figure()

                            # Historical data
                            fig.add_trace(go.Scatter(
                                x=st.session_state.ts_data.index,
                                y=st.session_state.ts_data.values.flatten(),
                                name='Historical',
                                line=dict(color='blue')
                            ))

                            # Forecast
                            fig.add_trace(go.Scatter(
                                x=forecast_result['forecast']['ds'],
                                y=forecast_result['forecast']['yhat'],
                                name='Forecast',
                                line=dict(color='red')
                            ))

                            # Confidence intervals
                            fig.add_trace(go.Scatter(
                                x=forecast_result['forecast']['ds'],
                                y=forecast_result['forecast']['yhat_upper'],
                                fill=None,
                                mode='lines',
                                line_color='rgba(255,0,0,0.2)',
                                name='Upper Bound'
                            ))

                            fig.add_trace(go.Scatter(
                                x=forecast_result['forecast']['ds'],
                                y=forecast_result['forecast']['yhat_lower'],
                                fill='tonexty',
                                mode='lines',
                                line_color='rgba(255,0,0,0.2)',
                                name='Lower Bound'
                            ))

                        else:
                            # Plot ARIMA forecast
                            fig = go.Figure()

                            # Historical data
                            fig.add_trace(go.Scatter(
                                x=st.session_state.ts_data.index,
                                y=st.session_state.ts_data.values.flatten(),
                                name='Historical',
                                line=dict(color='blue')
                            ))

                            # Forecast
                            fig.add_trace(go.Scatter(
                                x=forecast_result['forecast_index'],
                                y=forecast_result['forecast'],
                                name='Forecast',
                                line=dict(color='red')
                            ))

                        fig.update_layout(
                            title=f"{forecast_method} Forecast ({forecast_periods} periods)",
                            xaxis_title="Date",
                            yaxis_title=st.session_state.ts_value_col
                        )

                        st.plotly_chart(fig, use_container_width=True)

                    else:
                        st.error(message)

        with tab4:
            st.subheader("Anomaly Detection")

            st.info("🚧 Anomaly detection for time series will be implemented in the next update.")

            # Placeholder for future implementation
            st.write("**Planned Features:**")
            st.write("- Statistical anomaly detection (ARIMA residuals)")
            st.write("- Seasonal anomaly detection")
            st.write("- Change point detection")
            st.write("- Interactive anomaly marking and removal")